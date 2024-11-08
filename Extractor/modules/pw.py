import requests
import math
from Extractor import app

async def get_otp(message, phone_no):
    url = "https://api.penpencil.co/v1/users/get-otp"
    query_params = {"smsType": "0"}

    headers = {
        "client-id": "5eb393ee95fab7468a79d189",
        "client-version": "12.84",
        "Client-Type": "MOBILE",
        "randomId": "e4307177362e86f1",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
    }

    payload = {
        "username": phone_no,
        "countryCode": "+91",
        "organizationId": "5eb393ee95fab7468a79d189"
    }

    try:
        response = requests.post(url, params=query_params, headers=headers, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        await message.reply_text("**Failed to Generate OTP**")

async def get_token(message, phone_no, otp):
    url = "https://api.penpencil.co/v3/oauth/token"
    payload = {
        "username": phone_no,
        "otp": otp,
        "client_id": "system-admin",
        "client_secret": "KjPXuAVfC5xbmgreETNMaL7z",
        "grant_type": "password",
        "organizationId": "5eb393ee95fab7468a79d189",
        "latitude": 0,
        "longitude": 0
    }

    headers = {
        "content-type": "application/json; charset=UTF-8",
        "randomid": "e4307177362e86f1",
        "user-agent": 'Android',
        "Host": "api.penpencil.xyz",
        "authorization": "Bearer",
        "client-id": "5eb393ee95fab7468a79d189",
        "client-version": "12.84",
        "client-type": "MOBILE",
        "device-meta": "{APP_VERSION:12.84,DEVICE_MAKE:Asus,DEVICE_MODEL:ASUS_X00TD,OS_VERSION:6,PACKAGE_NAME:xyz.penpencil.physicswalb}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        resp = response.json()
        token = resp['data']['access_token']
        return token
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        await message.reply_text("**Failed to Generate Token**")

async def pw_mobile(app, message):
    user_input = await app.ask(message.chat.id, text="**ENTER YOUR PW MOBILE NO. WITHOUT COUNTRY CODE.**")
    phone_no = user_input.text
    await user_input.delete()
    await get_otp(message, phone_no)
    
    otp_input = await app.ask(message.chat.id, text="**ENTER YOUR OTP SENT ON YOUR MOBILE NO.**")
    otp = otp_input.text
    await otp_input.delete()
    token = await get_token(message, phone_no, otp)
    
    if token:
        await message.reply_text(f"**YOUR TOKEN** => `{token}`")
        await pw_login(app, message, token)

async def pw_token(app, message):
    token_input = await app.ask(message.chat.id, text="**ENTER YOUR PW ACCESS TOKEN**")
    token = token_input.text
    await token_input.delete()
    await pw_login(app, message, token)

async def pw_login(app, message, token):
    headers = {
        'Host': 'api.penpencil.co',
        'authorization': f"Bearer {token}",
        'client-id': '5eb393ee95fab7468a79d189',
        'client-version': '12.84',
        'user-agent': 'Android',
        'randomid': 'e4307177362e86f1',
        'client-type': 'MOBILE',
        'device-meta': '{APP_VERSION:12.84,DEVICE_MAKE:Asus,DEVICE_MODEL:ASUS_X00TD,OS_VERSION:6,PACKAGE_NAME:xyz.penpencil.physicswalb}',
        'content-type': 'application/json; charset=UTF-8',
    }

    params = {
        'mode': '1',
        'filter': 'true',
        'organisationId': '5eb393ee95fab7468a79d189',
        'limit': '20',
    }

    try:
        response = requests.get('https://api.penpencil.co/v3/batches/my-batches', params=params, headers=headers)
        response.raise_for_status()
        batches = response.json()["data"]
        
        batch_info = "**You have these Batches :-\n\nBatch ID   :   Batch Name**\n\n"
        
        for batch in batches:
            batch_info += f"**{batch['name']}**   :   `{batch['_id']}`\n"
        
        await message.reply_text(batch_info)
        
        batch_id_input = await app.ask(message.chat.id, text="**Now send the Batch ID to Download**")
        batch_id = batch_id_input.text
        await batch_id_input.delete()
        
        response_details = requests.get(f'https://api.penpencil.co/v3/batches/{batch_id}/details', headers=headers)
        subjects = response_details.json().get('data', {}).get('subjects', [])
        
        subject_info = "**Subject   :   SubjectId**\n\n"
        subject_ids = ""
        
        for subject in subjects:
            subject_info += f"**{subject.get('subject')}**   :   `{subject.get('subjectId')}`\n"
            subject_ids += f"{subject.get('subjectId')}&"
        
        await message.reply_text(subject_info)
        
        subject_ids_input = await app.ask(message.chat.id, text=f"Now send the **Subject IDs** to Download\n\nSend like this **1&2&3&4** so on\nor copy paste or edit **below ids** according to you :\n\n**Enter this to download full batch :-**\n`{subject_ids}`")
        raw_subject_ids = subject_ids_input.text
        await subject_ids_input.delete()
        
        selected_subjects = raw_subject_ids.split('&')
        subject_count_info = ""
        
        for subject_id in selected_subjects:
            for subject in subjects:
                if subject.get('subjectId') == subject_id:
                    subject_count_info += f"{subject.get('subjectId')}:{subject.get('tagCount')}&"

        resolution_input = await app.ask(message.chat.id, text="**Enter resolution**")
        resolution = resolution_input.text
        await resolution_input.delete()
        
        try:
            subject_count_list = subject_count_info.split('&')
            for subject_info in subject_count_list:
                if not subject_info:
                    continue
                
                subject_id, tagcount = subject_info.split(':')
                total_pages = math.ceil(int(tagcount) / 20)

                for page in range(1, total_pages + 1):
                    params = {'page': str(page)}
                    response_topics = requests.get(f"https://api.penpencil.xyz/batches/{batch_id}/subject/{subject_id}/topics", params=params, headers=headers)
                    topics_data = response_topics.json()["data"]
                    
                    with open("mm.txt", 'a') as f:
                        for topic in topics_data:
                            f.write(f"{topic}\n")

            await app.send_document(message.chat.id, document="mm.txt")
        except Exception as e:
            await message.reply_text(str(e))
    except requests.exceptions.RequestException as e:
        await message.reply_text(f"**Error during request: {str(e)}**")
