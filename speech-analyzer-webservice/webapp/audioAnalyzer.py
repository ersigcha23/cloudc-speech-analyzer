import requests
import json
import os

API_ENDPOINT = os.environ.get('URL_TEXTANALYZER_ENDPOINT')
API_KEY = "XXXXXXXXXXXXXXXXX"

class AudioAnalyzer:
    def extractPhrases(id, text):
        API_ENDPOINT = os.environ.get('URL_TEXTANALYZER_ENDPOINT')
        try:
            data = {'text': text,
            'language': 'spanish'}
            r = requests.post(url=API_ENDPOINT, data=data)

            # extracting response text
            analysis = json.loads(r.text)
            #transcription = r.text
            #print("The result of the transcription is:%s" % transcription['text'])
            return json.dumps({'id': id,
                'result': analysis}, ensure_ascii=False)
        except requests.exceptions.RequestException as e:
            print("ERROR: An exception ocurred while processing the HTTP request.")
            return json.dumps({'error': "An exception ocurred while processing the HTTP request."} )