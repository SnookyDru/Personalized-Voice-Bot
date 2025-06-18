import os, base64
import streamlit as st
import speech_recognition as sr
import pyttsx3
from google import genai
from google.genai import types

# Set API key
os.environ["GOOGLE_API_KEY"] = st.secrets.get("GOOGLE_API_KEY")
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

WAV_OUT = "resp.wav"

def transcribe_audio(uploaded_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(uploaded_file) as src:
        audio = recognizer.record(src)
    try:
        return recognizer.recognize_google(audio)
    except:
        return ""

def gemini_chat(text):
    resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction="""You are me—a thoughtful, warm, lightly humorous conversationalist...""",  # trimmed for brevity
            max_output_tokens=200,
            temperature=0.7,
        )
    )
    return resp.text

def speak_text_to_wav(text, outpath=WAV_OUT):
    engine = pyttsx3.init()
    engine.save_to_file(text, outpath)
    engine.runAndWait()

def embed_autoplay_audio(path):
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    audio_html = f'<audio autoplay><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

# Streamlit UI
st.title("🎙️ Home.LLC Project: Voice Bot That Speaks Like Me")
st.caption("Upload a WAV file to ask a question and get a personalized voice response.")
st.caption("-- Dhruv Kumar")

uploaded = st.file_uploader("🎧 Upload your voice question (WAV format)", type=["wav"])

if uploaded is not None:
    st.audio(uploaded, format='audio/wav')
    with st.spinner("Transcribing..."):
        user_text = transcribe_audio(uploaded)
    st.markdown(f"**You said:** {user_text or '_(unrecognized)_'}")

    if not user_text:
        st.error("Sorry, couldn't understand your voice.")
    else:
        with st.spinner("Generating Gemini reply..."):
            reply = gemini_chat(user_text)
        st.markdown(f"**Bot says:** {reply}")
        with st.spinner("Speaking..."):
            speak_text_to_wav(reply)
        embed_autoplay_audio(WAV_OUT)
