##### 기본 정보 입력 #####
import streamlit as st
from audiorecorder import audiorecorder
import openai
import os
from datetime import datetime
from gtts import gTTS
import base64

##### 기능 구현 함수 #####
def STT(audio):
    filename='input.mp3'
    audio.export(filename, format="mp3")
    audio_file = open(filename, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    audio_file.close()
    os.remove(filename)
    return transcript["text"]

def ask_gpt(prompt, model):
    response = openai.ChatCompletion.create(model=model, messages=prompt)
    system_message = response["choices"][0]["message"]
    return system_message["content"]

def TTS(response):
    filename = "output.mp3"
    tts = gTTS(text=response, lang="en")  # 한국어 'ko'를 'en'으로 변경
    tts.save(filename)

    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="True">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    os.remove(filename)

##### 메인 함수 #####
def main():
    st.set_page_config(
        page_title="English Chat Program",
        layout="wide")

    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in English"}]  # 한국어 문장을 영어로 수정

    if "check_reset" not in st.session_state:
        st.session_state["check_reset"] = False

    st.header("English Chat Program")
    st.markdown("---")

    with st.expander("About the English Chat Program", expanded=True):
        st.write(
        """     
        - The UI of the English Chat Program uses Streamlit.
        - STT (Speech-To-Text) uses OpenAI's Whisper AI.
        - Answers are generated using OpenAI's GPT model.
        - TTS (Text-To-Speech) uses Google's Google Translate TTS.
        """
        )

        st.markdown("")

    with st.sidebar:
        openai.api_key = st.text_input(label="OPENAI API Key", placeholder="Enter Your API Key", value="zRZHbfPv333AyuMmkzGuT3BlbkFJWnWQQk37Qa0UnCgXuP7b", type="password")

        st.markdown("---")

        model = st.radio(label="GPT Model", options=["gpt-4", "gpt-3.5-turbo"])

        st.markdown("---")

        if st.button(label="Reset"):
            st.session_state["chat"] = []
            st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in English"}]  # 한국어 문장을 영어로 수정
            st.session_state["check_reset"] = True
            
    col1, col2 =  st.columns(2)
    with col1:
        st.subheader("User")
        audio = audiorecorder("Click and Speak", "Recording...")
        if (audio.duration_seconds > 0) and (st.session_state["check_reset"]==False):
            st.audio(audio.export().read())
            question = STT(audio)

            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"]+ [("user", now, question)]
            st.session_state["messages"] = st.session_state["messages"]+ [{"role": "user", "content": question}]

    with col2:
        st.subheader("Assistant")
        if  (audio.duration_seconds > 0)  and (st.session_state["check_reset"]==False):
            response = ask_gpt(st.session_state["messages"], model)

            st.session_state["messages"] = st.session_state["messages"]+ [{"role": "system", "content": response}]

            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"]+ [("assistant", now, response)]

            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
            
            TTS(response)
        else:
            st.session_state["check_reset"] = False

if __name__=="__main__":
    main()
