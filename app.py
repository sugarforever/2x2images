from time import sleep
import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="2x2 Images")
st.title("2x2 Images")

def get_progress_text(percentage):
    return f"Image generation in progress ({percentage}%). Please wait."

def imagine(prompt_input, thenextleg_token):
    url = "https://api.thenextleg.io/v2/imagine"
    payload = json.dumps({
        "msg": prompt_input,
        "ref": "",
        "webhookOverride": ""
    })
    headers = {
        'Authorization': f'Bearer {thenextleg_token}',
        'Content-Type': 'application/json'
    }

    message_id = None
    response = requests.request("POST", url, headers=headers, data=payload)
    if (response.status_code == 200):
        json_response = json.loads(response.text)
        print(json_response)
        if (json_response["success"] == True):
            message_id = json_response["messageId"]
    
    return message_id

def get_message(message_id, thenextleg_token):
    url = f"https://api.thenextleg.io/v2/message/{message_id}"
    headers = {
        'Authorization': f'Bearer {thenextleg_token}',
    }

    json_response = None

    while not json_response:
        response = requests.request("GET", url, headers=headers)
        if (response.status_code == 200):
            json_response = json.loads(response.text)
            print(json_response)
            break
    return json_response

def get_images(message_id, thenextleg_token):
    images = list()
    response_content = None
    while True:
        message = get_message(message_id, thenextleg_token)
        if (message["progress"] == 100):
            progress = message["progress"]
            progress_bar.progress(progress, text=get_progress_text(progress))

            images.extend(message["response"]["imageUrls"])
            response_content = message["response"]["content"]
            break
        else:
            progress = message["progress"]
            progress_bar.progress(progress, text=get_progress_text(progress))
    return (images, response_content)

with st.form("prompt_form"):
    st.write("TheNextLeg Driven Image Generation")
    thenextleg_token = st.text_input(label="API Token", value="", type="password")
    prompt_input = st.text_area(label="Prompt", value="")
    submitted = st.form_submit_button("Go")
    if submitted:
        with st.container():
            progress_bar = st.progress(0, text=get_progress_text(0))
            message_id = imagine(prompt_input, thenextleg_token)
            sleep(2)
            (images, response_content) = get_images(message_id, thenextleg_token)
            st.text(response_content)

        with st.container():
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
