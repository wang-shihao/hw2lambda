import json
import boto3
import requests
import os
import logging

import inflect


def lambda_handler(event, context):

    print(event)
    # query_text = "show me tree"
    query_text = event["queryStringParameters"]['q']
    labels = getPhotoLabel(query_text)

    print(query_text)

    base_url = 'https://vpc-photos-rkisa6no36iownm37kejqzbziy.us-east-1.es.amazonaws.com'
    auth = ('coms6998','Coms6998!')
    headers = {'Content-Type': 'application/json'}

    paths_set = set()
    for label in labels:
        url = base_url + '/_search?q=labels:' + label
        response = requests.get(url, auth=auth, headers=headers)
        response = response.json()


        for info in response['hits']['hits']:
            photo_data = info['_source']
            photo_bucket = photo_data['bucket']
            photo_key = photo_data['objectKey']
            
            # check url format
            photo_url = 'https://{}.s3.amazonaws.com/{}'.format(photo_bucket, photo_key)
            paths_set.add(photo_url)

    photo_paths = list(paths_set)
    print(photo_paths)

    lam_response = {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin":"*","Content-Type":"application/json"},
        "body": json.dumps(photo_paths),
        "isBase64Encoded": False
    }
    return lam_response

def getPhotoLabel(query_text):
    client = boto3.client('lex-runtime')
    lex_response = client.post_text(
        botName='photo_query',
        botAlias='$LATEST',
        userId='coms6998',
        inputText=query_text)
    labels = []
    if 'slots' in lex_response:
        slots = lex_response['slots']
        for key,value in slots.items():
            if value!=None:
                p = inflect.engine()
                if p.singular_noun(value):
                    singular_word = p.singular_noun(value)
                else:
                    singular_word = value

                # singular_value =  value.rstrip('s')
                labels.append(singular_word)
    return labels