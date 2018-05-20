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
    """ Entry point of Lambda function.
    Args:
        event: HTTP request.
    Returns:
        advice: string. Advice for the medical checkup image.
    """
    # Generate json from base64-encoded image.
    data = generate_json_from_base64_image(event['image'])

    # Get response from Cloud Vision API
    response = get_response_from_cv_api(data)

    # Load response text as json.
    text_result = json.loads(response.text)

    # Extract description.
    description = text_result['responses'][0]['textAnnotations'][0]['description']

    # Parse description
    parsed = parse_description(description)

    # Generate advice.
    advice = generate_advice(parsed)

    return advice


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
    feature_json_obj = [{'type': get_detection_type(5),
                         'maxResults': 50,
                        }
                       ]

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
    """ Return the Vision API symbol corresponding to the given number.
    detect_num: int. Map detect type.
    """
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


def parse_description(description):
    """ Parse description.
    Args:
        description: str.
    Returns:
        parsed: list. parsed description.
    """
    parsed = description.split('\n')
    return parsed

# TO BE CREATED.
JARGON_MAP = {'hdlc': 'HDLコレステロール (善玉コレステロール): 血管内のコレステロールを回収する役割があります'}
ADVICE_MAP = {'hdlc_low': '善玉コレステロール＝血管内のコレステロールを回収する役割があります'}


def generate_advice(parsed):
    """ Generate advice.
    Args:
        parsed: list. parsed ocr text.
    Returns:
        advice: string. advice for health.
    """
    # Get item name, lower bound and upper bound of standard and actual value.
    ind = 32
    row = parsed[ind]
    item, l_bound, u_bound = row.split('-')
    l_bound = int(l_bound)
    u_bound = int(u_bound)
    item = item[2:]

    # Get actual value.
    actual = parsed[ind + 2]
    act, _ = actual.split(' ')
    act = int(act)

    # TO DO: CREATE MAP LATER.
    reformed_item = ''
    if item == 'H D L . C':
        reformed_item = 'HDL.C'

    # TO DO: CREATE MAP LATER.
    advice = ''
    if reformed_item == 'HDL.C' and l_bound <= act and act <= u_bound:
        advice = '問題ありません'
    elif reformed_item == 'HDL.C' and l_bound >= act:
        advice = "HDL.Cが基準値を下回っています（基準値: {} - {}, あなたの値: {}）。\n【結果の解釈】\nHDLコレステロールは善玉コレステロールと呼ばれ、血管内の脂質を回収する役割があります。HDLコレステロールが低いと、血管内に脂肪が増え、動脈硬化などを引き起こします。\n【改善策】\n薬ではなく、まずは運動と食事を改善します。運動とは、例えば週に2,3日に30分運動する時間を設けることが推奨されます。食事は油物を避けることが勧められます。\n【今後の方針】\n運動・食事習慣を改善して半年〜1年後に再度検査を行い、HDLコレステロールが改善していないようであれば医療機関での詳しい検査を勧めます。\n\n\n\n【医師からの一言】この結果であれば、医学的に問題はありません。\n病院に受診しなくても大丈夫です。\n安心してください。\n".format(l_bound, u_bound, act)
    return advice

