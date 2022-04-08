#!/usr/bin/python3

from selenium import webdriver 
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
from hashlib import blake2b
import json
import os.path
import requests
import pickle
from urllib.parse import urlparse

def get_driver():
    # proxy instructions from https://medium.com/ml-book/multiple-proxy-servers-in-selenium-web-driver-python-4e856136199d
    # from http_request_randomizer.requests.proxy.requestProxy import RequestProxy

    #req_proxy = RequestProxy() #you may get different number of proxy when  you run this at each time
    #proxies = req_proxy.get_proxy_list() #this will create proxy list

    opts = Options()
    opts.headless = False
    #assert opts.headless

    driver = webdriver.Firefox(executable_path= "/home/martin/miniconda3/envs/selenium/bin/geckodriver", options=opts)
    return driver

def login_manual(driver):
    driver.get("https://www.vn.at")

    username = "undisclosed"
    password = "undisclosed"

    action = webdriver.ActionChains(driver)
    login = driver.find_element(By.CSS_SELECTOR, 'a.menu-item.login')
    login.click()
    time.sleep(5)
    fusername = driver.find_element(By.XPATH, "//label[@for='username']/input")
    fpassword = driver.find_element(By.XPATH, "//label[@for='password']/input")
    button = driver.find_element(By.XPATH, "//div[@class='paywall-form max-w-full']//button")
    fusername.send_keys(username)
    fpassword.send_keys(password)
    time.sleep(0.2)
    action.move_to_element(button)
    action.click(on_element = button)
    action.perform()

    pickle.dump( driver.get_cookies() , open("cookies.pkl","wb"))
    time.sleep(2)

#login_manual()

def login_cookie():
    driver.get("https://www.vn.at")
    time.sleep(1)
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
        print(cookie)
    driver.get("https://www.vn.at")
    time.sleep(1)

def get_grundundboden_url_list():
    print(f"Getting all Grundundboden links")
    driver.get("https://www.vn.at/tags/grund-und-boden")
    
    def count_articles(dr):
        li = []
        for article in dr.find_elements(By.XPATH, "//main//article"):
            di = {}
            href = article.find_element(By.XPATH, ".//a")
            hr = href.get_attribute('href')
            di['href'] = hr
            
            hBlake = blake2b(key=b'pseudorandom key', digest_size=20)
            hBlake.update(str(hr).encode('utf-8'))
            fid = hBlake.hexdigest()
            di['uid'] = fid

            fn_json = fid + ".json"
            di['fn'] = fn_json
            
            li.append(di)

        print(f"found {len(li)} documents")
        return li

    script = """
    var lastScrollHeight = 0; 
    function autoScroll() { 
      var sh = document.documentElement.scrollHeight; 
      if (sh != lastScrollHeight) { 
        lastScrollHeight = sh; 
        document.documentElement.scrollTop = sh; 
      } 
    } 
    window.setInterval(autoScroll, 100); 
    """

    driver.execute_script(script)

    slp = 1.5
    li = []
    last_len = 0
    cont = True
    while cont:
        last_len = len(li)
        li = count_articles(driver)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        if last_len == 0:
            time.sleep(5)
        time.sleep(slp)

        print(f"Storing {len(li)} urls to file")
        fn_urls = "urls.json"
        with open(fn_urls, 'w', encoding='utf8') as json_file:
            json.dump(li, json_file, ensure_ascii=False)

        if len(li) == last_len:
            break

def getall_grundundboden(driver, fn_json):
    print(f"Getting all individual Grundundboden documents")
    with open(fn_json, 'r', encoding='utf8') as json_file:
        di = json.load(json_file)

    i=0
    for el in di:
        print(f"Link #{i}: {el['href']}")
        
        fetch_individual_grundundboden_url(driver, el['href'], el['uid'], el['fn'], False)

        #article_xpath_orig = "/html/body/div[1]/div/div/main/div[2]/div/article/div/div[3]/div/div[2]/p"
        #picture_xpath = "/html/body/div[1]/div/div/main/div[2]/div/article/div/div[3]/div/div[3]/figure/img"
        #button = driver.find_element_by_xpath("//div[@class='paywall-form max-w-full']//button")

        i+=1
        #if i>5:
        #    break
    

def fetch_individual_grundundboden_url(driver, url, uid, targetfn, overwrite = False):
    targetfn = "data/" + targetfn
    htmlfn = "data/" + uid + ".html"

    if os.path.isfile(targetfn) and os.path.isfile(targetfn) and not overwrite:
        print (f" --> File {targetfn} exists")
    else:
        print (f" --> File {targetfn} does not exist")

        driver.get(url)
        time.sleep(0.5)
        full_page_source = driver.page_source
        with open(htmlfn, 'w', encoding='utf8') as json_file:
            json.dump(full_page_source, json_file, ensure_ascii=False)

        article_xpath_real = "//article//div[@class='paywalled-content']//p"
        picture_xpath_real = "//article//div[@class='paywalled-content']//img"

        picture_url_li = driver.find_elements(By.XPATH, picture_xpath_real)

        di = {}
        di['url'] = url
        #di['X_page_source'] = full_page_source
        
        img_li = []
        i=0
        for img_el in picture_url_li:
            di_img = {}
            di_img['idx'] = i

            picture_url = img_el.get_attribute('src')
            if picture_url[:5] == 'data:':
                orig_img_fn = '[embedded]'
                fn_img = uid + "-" + str(i) + "-embedded.base64"
                
                di_img['orig_fn'] = orig_img_fn
                di_img['filename'] = fn_img

                fn_img = "data/" + fn_img
                open(fn_img, 'w').write(picture_url)
            else:

                print(picture_url)
                di_img['url'] = picture_url

                a = urlparse(picture_url)
                print(a.path)                    # Output: /kyle/09-09-201315-47-571378756077.jpg
                print(os.path.basename(a.path))  # Output: 09-09-201315-47-571378756077.jpg
                orig_img_fn = os.path.basename(a.path)

                req = requests.get(picture_url, allow_redirects=True)

                fn_img = uid + "-" + orig_img_fn

                di_img['orig_fn'] = orig_img_fn
                di_img['filename'] = fn_img

                fn_img = "data/" + fn_img

                open(fn_img, 'wb').write(req.content)
                img_li.append(di_img)
                i+=1
        
        di['images'] = img_li
        
        article_li = driver.find_elements(By.XPATH, article_xpath_real)
        if len(article_li) == 0:
            print(f"no articles, not writing anything")
            return
        
        articles = []
        i=0
        for art_el in article_li:
            di_art = {}
            outerHtml = art_el.get_attribute('outerHTML')
            innerHtml = art_el.get_attribute('innerHTML')
            text = art_el.text

            di_art['idx'] = i
            di_art['text'] = text
            di_art['outerHTML'] = outerHtml
            di_art['innerHtml'] = innerHtml
            articles.append(di_art)
            i += 1
        
        di['articles'] = articles
        #fn_json = "/data/" + fid + ".json"

        with open(targetfn, 'w', encoding='utf8') as json_file:
            json.dump(di, json_file, ensure_ascii=False)
        

    
def get_page():
    content = driver.find_element_by_id('content')
    header = content.find_element_by_class_name('a-z_header')

    hdr = []
    for el in header.find_elements(By.XPATH, './/span'):
        hdr.append(el.text)
    hdr.append('href')
    hdr.append('uid')

    board = content.find_element_by_class_name('link-list_big')

    for row in board.find_elements(By.XPATH, './/li'):
        r = []
        for el in row.find_elements(By.XPATH, './/span'):
            r.append(el.text)

        href = row.find_element(By.XPATH, './/a')
        hr = href.get_attribute('href')
        r.append(hr)

        hBlake = blake2b(key=b'pseudorandom key', digest_size=20)
        hBlake.update(str(r).encode('utf-8'))
        fid = hBlake.hexdigest()
        r.append(fid)

        fn_json = "/data/" + fid + ".json"
        fn_pdf = "/data/" + fid + ".pdf"

        di = dict(zip(hdr, r))
        s = json.dumps(di, ensure_ascii=False).encode('utf8')

        print(s.decode().encode('ascii', 'ignore').decode('ascii'))
        if os.path.isfile(fn_json) and os.path.isfile(fn_pdf):
            pass
            print (" --> Files exist")
        else:
            print (" --> Files do not exist")
            req = requests.get(hr, allow_redirects=True)
            open(fn_pdf, 'wb').write(req.content)
            with open(fn_json, 'w', encoding='utf8') as json_file:
                json.dump(di, json_file, ensure_ascii=False)


driver = get_driver()
login_manual(driver)
#login_cookie()
#get_page()
get_grundundboden_url_list()
getall_grundundboden(driver, "urls.json")

exit(1)

driver.close()
