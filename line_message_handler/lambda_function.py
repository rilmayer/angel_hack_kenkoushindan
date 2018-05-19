import os
import json
import requests
import base64

print('Loading function')

LINE_API_ENDPOINT = 'https://api.line.me/v2/bot/message/reply'

LINE_API_HEADERS = {
    'Authorization': 'Bearer ' + os.environ['LINE_CHANNEL_ACCESS_TOKEN'],
    'Content-type': 'application/json'
}

OCR_API_ENDPOINT = 'https://3d6jfzwdh9.execute-api.ap-northeast-1.amazonaws.com/prod/ocr'

# 画像を北原APIで取得
def image_to_text(image):
    payload = {'image': base64.b64encode(image).decode('utf-8')}
    response = requests.post(OCR_API_ENDPOINT, data=json.dumps(payload))
    return response.text

# 質問ハンドリング関数
def question_handller(question):
    if 'コレステロール' in question:
        return '食事・運動で改善します。'
    elif 'AST' in question or 'ALT' in question:
        return "肝臓の機能などを反映しています。お酒を飲むだけで上がる人もいます。ただし、特異性が低いので、これが上がってるだけではなんの病気かは特定できません。100を越えるような場合は症状がなくても病院に受診をお勧めします。"
    elif 'アルブミン' in question:
        return '栄養の値を表わします。低いとむくみの原因になったりもします。個人差があるので、前回と比べて減ってるかどうかが大事です。もし症状があれば受診を勧めます。ない場合は肝臓の機能をチェックして異常があれば、受診を勧めます。'
    elif 'γGTP' in question:
        return '主に肝臓の機能を表わします。お酒を飲む頻度をチェックする必要があります。お酒をそんなに飲んでいないのに上がっているときは注意が必要です'
    elif 'ビリルビン' in question:
        return '胆汁に含まれる成分です。この値が高いと黄色くなる黄疸になります。体に異常がなければ高くなることはほとんどないので、1.5くらいを超えていたら一度受診を勧めます。'
    elif 'HBV' in question or 'HC' in question:
        return '肝炎ウイルスを表わします。以前にかかっておらず、新規で見つかった場合は必ず受診しましょう。ほっておくと肝硬変にいたる危険性があります。輸血や性交渉でうつるといわれますが、恥ずかしいことではないので、隠さずにきちんと病院にかかりましょう'
    elif 'アミラーゼ' in question:
        return '膵臓の機能を表わします。お酒飲みや薬の副作用でも上がることがあります。3桁後半になると膵炎をきたしている可能性が高いので必ず受診しましょう。'
    elif 'CRP' in question:
        return '体の中の炎症を表す数値です。基本的にはゼロに近いですが、感染や関節の炎症などで高くなります。わかるのは炎症がある事だけなので、この値だけで病気を診断することはできません。'
    else:
        return 'すみません、答えられない質問です。'


#LINEから画像データを取得
def getImageLine( id ):
    line_url = 'https://api.line.me/v2/bot/message/'+ id +'/content'
    result = requests.get(line_url, headers=LINE_API_HEADERS)
    image_string = result.content
    return image_string

def lambda_handler(event, context):
    for event in event['events']:
        reply_token = event['replyToken']
        message = event['message']
        if message['type'] == 'image':
            id = message['id']
            file = getImageLine(id)
            res = image_to_text(file)
            message = "健康診断データを読み込み中だよ。\n(Now Loading: helth chek data) " + str(res)
        elif message['type'] == 'text':
            message = question_handller(message['text'])

        payload = {
            'replyToken': reply_token,
            'messages': []
        }
        payload['messages'].append({
                'type': 'text', 'text': str(message)
            })
        response = requests.post(LINE_API_ENDPOINT, headers=LINE_API_HEADERS, data=json.dumps(payload))
        print(response.status_code)
    return 'Hello from Lambda'
