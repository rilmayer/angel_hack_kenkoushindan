# -*- coding: utf-8 -*-
import requests
import argparse
import base64
import json
import sys
import os

API_KEY = os.getenv("DR_MEDICAL_CHECKUP_API_KEY", "api key not exist")
print(API_KEY)

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = '/Users/k_kitahara/workspace/angel_hack_kenkoushindan/'

DETECTION_TYPES = [
    'TYPE_UNSPECIFIED',
    'FACE_DETECTION',
    'LANDMARK_DETECTION',
    'LOGO_DETECTION',
    'LABEL_DETECTION',
    'TEXT_DETECTION',
    'SAFE_SEARCH_DETECTION',
]


def generate_infiletxt(path_to_image=BASE_DIR+'/data/google.jpg', infiletxt_path=BASE_DIR+'/data/visioninfile.txt'):
    """ Generate infiletxt to be requested Cloud Vision API.
    Args:
        path_to_image: string. Path to image.
            ex) /Users/username/workspace/fuga.jpg
        infiletxt_path: string. Output path.
            ex) /Users/username/workspace/visioninfile.txt
    """
    str = "{image_path} 5:10".format(image_path=path_to_image)
    with open(infiletxt_path, "w") as f:
        f.write(str)


def generate_json(input_filename=BASE_DIR+'/data/visioninfile.txt', output_filename=BASE_DIR+'/data/vision.json'):
    """ Translates the input file into a json output file.
    Args:
        input_filename: a file object, containing lines of input to convert.
            ex) /Users/username/workspace/visioninfile.txt
        output_filename: the name of the file to output the json to.
            ex) /Users/username/workspace/vision.json
    """
    with open(input_filename, 'r') as input_file:
        print(input_file)
        # Collect all requests into an array - one per line in the input file
        request_list = []
        for line in input_file:
            # The first value of a line is the image. The rest are features.
            image_filename, features = line.lstrip().split(' ', 1)

            # First, get the image data
            with open(image_filename, 'rb') as image_file:
                content_json_obj = {
                    'content': base64.b64encode(image_file.read()).decode('UTF-8')
                }

            # Then parse out all the features we want to compute on this image
            feature_json_obj = []
            for word in features.split(' '):
                feature, max_results = word.split(':', 1)
                feature_json_obj.append({
                    'type': get_detection_type(feature),
                    'maxResults': int(max_results),
                })

            # Now add it to the request
            request_list.append({
                'features': feature_json_obj,
                'image': content_json_obj,
            })

    # Write the object to a file, as json
    with open(output_filename, 'w') as output_file:
        json.dump({'requests': request_list}, output_file)


def get_detection_type(detect_num):
    """ Return the Vision API symbol corresponding to the given number."""
    detect_num = int(detect_num)
    if 0 < detect_num < len(DETECTION_TYPES):
        return DETECTION_TYPES[detect_num]
    else:
        return DETECTION_TYPES[0]


FILE_FORMAT_DESCRIPTION = '''
Each line in the input file must be of the form:

    file_path feature:max_results feature:max_results ....

where 'file_path' is the path to the image file you'd like
to annotate, 'feature' is a number from 1 to %s,
corresponding to the feature to detect, and max_results is a
number specifying the maximum number of those features to
detect.

The valid values - and their corresponding meanings - for
'feature' are:

    %s
'''.strip() % (
    len(DETECTION_TYPES) - 1,
    # The numbered list of detection types
    '\n    '.join(
        # Don't present the 0th detection type ('UNSPECIFIED') as an option.
        '%s: %s' % (i + 1, detection_type)
        for i, detection_type in enumerate(DETECTION_TYPES[1:])))


def get_response(json_file_path=BASE_DIR+'/data/vision.json'):
    """ Get response from Cloud Vision API.
    Args:
        json_file_path: string. json data including image info.
    Returns:
        response: Response class.
    """
    data = open(json_file_path, 'rb').read()

    url = 'https://vision.googleapis.com/v1/images:annotate?key={}'.format(API_KEY)

    response = requests.post(url=url, data=data, headers={'Content-Type': 'application/json'})

    return response
