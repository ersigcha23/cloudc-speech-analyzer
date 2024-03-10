import requests
import json
import os

# defining the api-endpoint
API_ENDPOINT = os.environ.get('URL_WHISPER_SERVICE_ENDPOINT')
#file_path = "media/audio-test1.mp3"


class AudioTranscriptor:

    def transcribe(file_path):
        API_ENDPOINT = os.environ.get('URL_WHISPER_SERVICE_ENDPOINT')
        print(API_ENDPOINT)
        # sending post request and saving response as response object
        try:
            with open(file_path, "rb") as file:
                files = {'audio_file': file}
                r = requests.post(url=API_ENDPOINT, files=files)

            # extracting response text        
            transcription = json.loads(r.text)
            #transcription = r.text
            #print("The result of the transcription is:%s" % transcription['text'])
            return json.dumps({'id': os.path.basename(file_path).split('/')[-1],
                'result': transcription['text']}, ensure_ascii=False)
        except FileNotFoundError:
            print("ERROR: The file was not found.")
            return json.dumps({'error': "The file was not found."} )
        except requests.exceptions.RequestException as e:
            print("ERROR: An exception ocurred while processing the HTTP request.")
            return json.dumps({'error': "An exception ocurred while processing the HTTP request."} )


