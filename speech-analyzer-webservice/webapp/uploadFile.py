import os
import boto3
from botocore.exceptions import ClientError
import sys
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import socket
socket.setdefaulttimeout(600)  # Timeout de socket (600 segundos)
import random
import requests
import string
import json
from dotenv import load_dotenv

from audioTranscriptor import AudioTranscriptor
from audioAnalyzer import AudioAnalyzer

load_dotenv('.env')
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB limit
app.config.from_pyfile('settings.py')

transcriptor=AudioTranscriptor()
analyzer=AudioAnalyzer()

def uploadFileS3(fsSourceFileName,bkDestinationFileName):
    s3Resource=boto3.resource("s3")

    try:
        """
        fsSourceFileName: file system bucket object name
        bkDestinationFileName: object name destination in bucket
        
        """

        print("\n\nUPLOADING FILE")
        #load file into memory
        data = open(fsSourceFileName, "rb")
        BUCKET_NAME = "finalmfsxes"
        s3Resource.Bucket(BUCKET_NAME).put_object(Key = bkDestinationFileName, Body = data)
        msg_s3='Uploaded file S3'
        status_s3="200"
        return jsonify({"message_s3":msg_s3,"status_s3":status_s3,"s3FileName":bkDestinationFileName})
      
    except Exception as e:
        print(f"Error processing request: {e}")
        msg_s3='S3 Error'
        status_s3='500'
        return jsonify({"message_s3":msg_s3,"status_s3":status_s3})
   
def invokeLambdaUsingBoto3(functionName, payload):
    """
    Invokes a Lambda function by using the boto3 package
    """
    lambdaClient = boto3.client('lambda','sa-east-1')

    response = lambdaClient.invoke(
        FunctionName=functionName,
        Payload=json.dumps(payload),
    )

    print(f"\n\nResponse from {functionName}:\n{response['Payload'].read().decode('utf-8')}")


def invokeLambdaUsingApiRequest(url, payload):
    """
    Invokes Lambda function through the API that exposes it
    """
    headers = {'Authorization': ''}
    r = requests.get(url, json=payload, headers=headers)
    print(f"\n\nResponse from {url}:\n{r.json()}")
    return r.json()


@app.route('/uploadFile', methods=['POST'])
def uploadFile():
    try:
        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        filename = secure_filename(file.filename)
        filename, extension = os.path.splitext(file.filename)
        # Generar una cadena aleatoria de 10 caracteres
        new_filename = "".join(random.choice(string.ascii_letters + string.digits) for i in range(10))+extension

        file.save(os.path.join('tmp/', new_filename))
    except Exception as e:
        print(f"Error uploading file: {e}")
        return jsonify({'error': str(e)}), 500
    
    uploadResult= uploadFileS3("tmp/"+new_filename,new_filename)
    #jsonUploadResult=json.loads(uploadResult)
    s3Filename=new_filename
    #return jsonify({"message_s3":msg_s3,"status_s3":status_s3,"s3FileName":new_filename }), 200
    transcriptionResult=AudioTranscriptor.transcribe("tmp/"+new_filename)
    jsonTranscriptionResult=json.loads(transcriptionResult)
    print(jsonTranscriptionResult)

    text_id=jsonTranscriptionResult["id"]
    transcribed_text=jsonTranscriptionResult["result"]

    analyzerResult=AudioAnalyzer.extractPhrases(text_id, transcribed_text)
    jsonAnalyzerResult=json.loads(analyzerResult)
    text_analyzed=jsonAnalyzerResult["result"]

    complete_result = {
        "s3FileName": s3Filename,
        "status_transcription": transcribed_text,
        "analysisResult": text_analyzed
    }

    invokeLambdaUsingBoto3("status_uploaded_file", complete_result)

    return jsonify(complete_result)

@app.route('/results', methods=['GET'])
def listResults():
    #LIST_API_URL="https://fggx025hmi.execute-api.sa-east-1.amazonaws.com/Trabajo/TrabajoFinal/listResults"
    LIST_API_URL=os.environ.get('URL_LISTRESULTS_ENDPOINT')
    try:
        payload= {
            "s3FileName": "2Kf0lvvI0H.mp3"
        }
        return invokeLambdaUsingApiRequest(LIST_API_URL,payload)
    except Exception as e:
        print(f"Error getting results list: {e}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/results/<s3FileName>', methods=['GET'])
def getResult(s3FileName):
    #SINGLERESULT_API_URL="https://fggx025hmi.execute-api.sa-east-1.amazonaws.com/Trabajo/TrabajoFinal/queryResult"
    SINGLERESULT_API_URL=os.environ.get('URL_SINGLERESULT_ENDPOINT')
    try:
        payload= {
            "s3FileName": s3FileName
        }
        result = invokeLambdaUsingApiRequest(SINGLERESULT_API_URL,payload)
        return result
    except Exception as e:
        print(f"Error getting result by filename: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(port=5001, host='0.0.0.0')