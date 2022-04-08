# Prodigy:

## the base annotation -- how 2 start
prodigy ner.manual ner_grund blank:de ./grund.jsonl --label ORT,VERKAEUFER,KAEUFER,GESAMTPREIS,FLAECHE,STRASSE,DATUM_VERTRAG,DATUM_VERBUECHERUNG,IMMO_TYP,QMPREIS,TERRASSENGROESSE --patterns ./pattern_ort.jsonl

## output annotations to ./annotations.jsonl
prodigy db-out ner_grund > ./annotations.jsonl

## training a spacy model
prodigy train spancatmodel_v1 --spancat spans_grund_base --gpu-id 0 -L

## visualize data
streamlit run visualize_data.py annotations.jsonl

