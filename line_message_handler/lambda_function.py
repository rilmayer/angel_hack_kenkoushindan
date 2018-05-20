import os
import json
import requests
import base64
import codecs

print('Loading function')

LINE_API_ENDPOINT = 'https://api.line.me/v2/bot/message/reply'

LINE_API_HEADERS = {
    'Authorization': 'Bearer ' + os.environ['LINE_CHANNEL_ACCESS_TOKEN'],
    'Content-type': 'application/json'
}

OCR_API_ENDPOINT = 'https://3d6jfzwdh9.execute-api.ap-northeast-1.amazonaws.com/prod/ocr'

# 画像解析APIで結果を取得
def image_to_text(image):
    payload = {'image': base64.b64encode(image).decode('utf-8')}
    response = requests.post(OCR_API_ENDPOINT, data=json.dumps(payload))
    #response.encoding = response.apparent_encoding
    return response.text

# 質問ハンドリング
def question_handller(question):
    if '項目' in question:
        return '以下の質問に回答できます。\n・コレステロール\n・AST\n・ALT\n・アルブミン\n・γGTP\n・ビリルビン\n・HBV\n・HCV\n・アミラーゼ\n・CRP\n・HDL\n・LDL'

    elif 'コレステロール' in question:
        return 'コレステロールが高いと血管内に脂肪が付着し、動脈硬化などを引き起こします。食事・運動で改善します。HDLコレステロールとLDLコレステロールがあります。'

    elif 'AST' in question:
        return '肝臓の機能などを反映しています。お酒を飲むだけで上がる人もいます。ただし、特異性が低いので、これが上がってるだけではなんの病気かは特定できません。100を越えるような場合は症状がなくても病院に受診をお勧めします。'

    elif 'ALT' in question:
        return '肝臓の機能などを反映しています。お酒を飲むだけで上がる人もいます。ただし、特異性が低いので、これが上がってるだけではなんの病気かは特定できません。100を越えるような場合は症状がなくても病院に受診をお勧めします。'

    elif 'アルブミン' in question:
        return '栄養の値を表わします。低いとむくみの原因になったりもします。個人差があるので、前回と比べて減ってるかどうかが大事です。もし症状があれば受診を勧めます。ない場合は肝臓の機能をチェックして異常があれば、受診を勧めます。'

    elif 'γGTP' in question:
        return '主に肝臓の機能を表わします。お酒を飲む頻度をチェックする必要があります。お酒をそんなに飲んでいないのに上がっているときは注意が必要です'

    elif 'ビリルビン' in question:
        return '胆汁に含まれる成分です。この値が高いと黄色くなる黄疸になります。体に異常がなければ高くなることはほとんどないので、1.5くらいを超えていたら一度受診を勧めます。'

    elif 'HBV' in question:
        return '肝炎ウイルスを表わします。以前にかかっておらず、新規で見つかった場合は必ず受診しましょう。ほっておくと肝硬変にいたる危険性があります。輸血や性交渉でうつるといわれますが、恥ずかしいことではないので、隠さずにきちんと病院にかかりましょう'

    elif 'HCV' in question:
        return '肝炎ウイルスを表わします。以前にかかっておらず、新規で見つかった場合は必ず受診しましょう。ほっておくと肝硬変にいたる危険性があります。輸血や性交渉でうつるといわれますが、恥ずかしいことではないので、隠さずにきちんと病院にかかりましょう'

    elif 'アミラーゼ' in question:
        return '膵臓の機能を表わします。お酒飲みや薬の副作用でも上がることがあります。3桁後半になると膵炎をきたしている可能性が高いので必ず受診しましょう。'

    elif 'CRP' in question:
        return '体の中の炎症を表す数値です。基本的にはゼロに近いですが、感染や関節の炎症などで高くなります。わかるのは炎症がある事だけなので、この値だけで病気を診断することはできません。'

    elif 'HDL' in question:
        return 'HDLコレステロール＝善玉コレステロール＝血管内のコレステロールを回収する役割があります。低下すると動脈硬化につながります。'

    elif 'LDL' in question:
        return 'LDLコレステロール＝悪玉コレステロール＝血管内にコレステロールを運ぶ役割があります。増加すると動脈硬化につながります。'

    elif '今日も1日' in question:
      return 'がんばるぞい！'

    elif '健康診断君' in question:
      return '俺は健康診断君。みんなの健康を守るぜ。'

    elif '不安' in question:
        hospital_description = get_hospital()
        return hospital

    else:
        return 'すみません、答えられない質問です。'

# get hospital
# 時間の都合上未実装
def get_hospital():
    hospital_description = 'この辺りには「社会福祉法人 三井記念病院」があります。\n受付時間は\n月曜日～金曜日 8：30～17：00\n土曜日 8：30～12：30\nhttps://www.mitsuihosp.or.jp/'
    return hospital_description


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
            message = codecs.decode(res, 'unicode-escape')
            message = message[0:500]
        elif message['type'] == 'text':
            message = question_handller(message['text'])
            message = message.replace('"', '')

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
