
# CS224u Course Project

The [Literature Review](https://github.com/cgpotts/cs224u/blob/master/projects.md#literature-review) should cover 7 (9) papers for a team of 2 (3).

# How to use prodigy

## the base annotation -- how 2 start

prodigy ner.manual ner_grund blank:de ./grund.jsonl --label ORT,VERKAEUFER,KAEUFER,GESAMTPREIS,FLAECHE,STRASSE,DATUM_VERTRAG,DATUM_VERBUECHERUNG,IMMO_TYP,QMPREIS,TERRASSENGROESSE --patterns ./pattern_ort.jsonl

## output annotations to ./annotations.jsonl

prodigy db-out ner_grund > ./annotations.jsonl