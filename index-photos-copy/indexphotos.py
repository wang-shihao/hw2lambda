import boto3
import json
import datetime
import requests


s3 = boto3.client('s3')
rek_client = boto3.client('rekognition', region_name='us-east-1')



def lambda_handler(event, context):
    # test demo
    print("event")
    print(event)
    s3_info = event['Records'][0]['s3']
    print("Info")
    print(s3_info)
    bucket_name = s3_info['bucket']['name']
    photo_name = s3_info['object']['key']
    print(photo_name, bucket_name)
    # get the labels of photo
    labels = detectLabels(bucket_name, photo_name)
    print("---------labels from Reko -------", labels)
    
    # get metadata from s3
    headObject = s3.head_object(Bucket=bucket_name, Key=photo_name)
    metaData = headObject['Metadata']
    modify_time = headObject['LastModified']
    
    for i, label in metaData.items():
        labels.append(str(label).lower())

    # create JSON array with labels
    json_object = {
        "objectKey": photo_name,
        "bucket": bucket_name,
        "createdTimestamp": modify_time.strftime("%y-%m-%d %H:%M:%S"),
        "labels": labels
    }
    print("-------------payload----------- ", json_object)

    # upload data to OpenSearch
    endpoint = 'https://search-photo-dcoxllgzvsuh2jzv6cj5soxojq.us-east-1.es.amazonaws.com/photo/_doc'
    headers = {'Content-Type': 'application/json'}
    auth = ('coms6998','Coms6998!')
    response = requests.post(endpoint, json = json_object, auth = auth, headers = headers)
    print(response)
    return {'response': str(response)}




def detectLabels(bucket, photo):
    print("Inside")
    print(photo, bucket)
    response = rek_client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}}, MinConfidence=75)
    labels = []
    for label in response['Labels']:
        labels.append(str(label['Name']).lower())
        if len(labels) > 4:
            break
    return labels





