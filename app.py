from time import sleep
import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
st.title("2x2 Images")

def get_progress_text(percentage):
    return f"Image generation in progress ({percentage}%). Please wait."

def imagine(prompt_input):
    url = "https://api.thenextleg.io/v2/imagine"
    payload = json.dumps({
        "msg": prompt_input,
        "ref": "",
        "webhookOverride": ""
    })
    headers = {
        'Authorization': f'Bearer {os.environ["THE_NEXT_LEG_TOKEN"]}',
        'Content-Type': 'application/json'
    }

    message_id = None
    response = requests.request("POST", url, headers=headers, data=payload)
    if (response.status_code == 200):
        json_response = json.loads(response.text)
        if (json_response["success"] == True):
            message_id = json_response["messageId"]
    
    return message_id

def get_message(message_id):
    url = f"https://api.thenextleg.io/v2/message/{message_id}"
    headers = {
        'Authorization': f'Bearer {os.environ["THE_NEXT_LEG_TOKEN"]}',
    }

    json_response = None

    while not json_response:
        response = requests.request("GET", url, headers=headers)
        if (response.status_code == 200):
            json_response = json.loads(response.text)
            break
    return json_response

def get_images(message_id):
    images = list()
    while True:
        message = get_message(message_id)
        if (message["progress"] == 100):
            progress = message["progress"]
            progress_bar.progress(progress, text=get_progress_text(progress))
            images.extend(message["response"]["imageUrls"])
            break
        else:
            progress = message["progress"]
            progress_bar.progress(progress, text=get_progress_text(progress))
    return images

with st.form("prompt_form"):
    st.write("AI Powered Image Generation")
    prompt_input = st.text_area("")
    submitted = st.form_submit_button("Go")
    if submitted:
        progress_bar = st.progress(0, text=get_progress_text(0))
        message_id = imagine(prompt_input)
        sleep(2)
        images = get_images(message_id)
        rows = []
        row = []
        for image in images:
            row.append(image)
            if len(row) == 2:
                rows.append(row)
                row = []
        for row in rows:
            col1, col2 = st.columns(2)
            if (row[0]):
                with col1:
                    st.image(row[0])

            if (row[1]):
                with col2:
                    st.image(row[1])
