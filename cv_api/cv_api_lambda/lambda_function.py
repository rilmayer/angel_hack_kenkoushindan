# -*- coding: utf-8 -*-
import requests
import json
import os

API_KEY = os.getenv("DR_MEDICAL_CHECKUP_API_KEY", "api key not exist")

DETECTION_TYPES = [
    'TYPE_UNSPECIFIED',
    'FACE_DETECTION',
    'LANDMARK_DETECTION',
    'LOGO_DETECTION',
    'LABEL_DETECTION',
    'TEXT_DETECTION',
    'SAFE_SEARCH_DETECTION',
]


def lambda_handler(event, context):
    data = generate_json_from_base64_image(event['image'])
    response = get_response_from_cv_api(data)
    return response.text


def generate_json_from_base64_image(base64_image):
    """ Translates the input file into a json text.
    Args:
        base64_image: string. base64-encoded image.
    Returns:
        json_data: string. json data.
    """
    # Content image
    content_json_obj = {'content': base64_image}

    # Detection type.
    detection_type = 5
    max_results = 30
    feature_json_obj = [{
        'type': get_detection_type(detection_type),
        'maxResults': max_results,
    }]

    # Now add it to the request
    request_list = []
    request_list.append({
        'features': feature_json_obj,
        'image': content_json_obj,
    })

    # To json
    data = json.dumps({'requests': request_list})

    return data


def get_detection_type(detect_num):
    """ Return the Vision API symbol corresponding to the given number."""
    detect_num = int(detect_num)
    if 0 < detect_num < len(DETECTION_TYPES):
        return DETECTION_TYPES[detect_num]
    else:
        return DETECTION_TYPES[0]


def get_response_from_cv_api(data):
    """ Get response from Cloud Vision API.
    Args:
        data: string: json data.
    Returns:
        response: Response from Cloud Vision API.
    """
    url = 'https://vision.googleapis.com/v1/images:annotate?key={}'.format(API_KEY)

    response = requests.post(url=url, data=data, headers={'Content-Type': 'application/json'})

    return response
