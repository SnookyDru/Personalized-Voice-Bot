import os, base64
import streamlit as st
import speech_recognition as sr
import pyttsx3
from google import genai
from google.genai import types

# Set your Gemini API key
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

WAV_OUT = "resp.wav"

def transcribe_audio_file(wav_file):
    r = sr.Recognizer()
    with sr.AudioFile(wav_file) as src:
        audio = r.record(src)
    try:
        return r.recognize_google(audio)
    except:
        return ""

def gemini_chat(text):
    resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=text,
        config=types.GenerateContentConfig(
            system_instruction="""
You are me—a thoughtful, warm, lightly humorous conversationalist.  
Keep answers personal, sincere, with gentle reflection and occasional humor...
""",
            max_output_tokens=200,
            temperature=0.7,
        )
    )
    return resp.text

def speak_text_to_wav(text, path=WAV_OUT):
    engine = pyttsx3.init()
    engine.save_to_file(text, path)
    engine.runAndWait()

def embed_autoplay_audio(path):
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    st.markdown(
        f'<audio autoplay><source src="data:audio/wav;base64,{b64}" type="audio/wav"></audio>',
        unsafe_allow_html=True,
    )

st.title("🎙️ Personalized Gemini Voice Bot")
st.caption("Speak, and the bot responds in my voice!")

audio_bytes = st.audio_input("🎤 Record your question")
if audio_bytes:
    # Let user preview
    st.audio(audio_bytes, format="audio/wav")

    # Save uploaded bytes to WAV file for transcription
    with open("user.wav", "wb") as f:
        f.write(audio_bytes.read())

    with st.spinner("Transcribing..."):
        user_text = transcribe_audio_file("user.wav")
    st.markdown(f"**You said:** {user_text or '_(unrecognized)_'}")

    if user_text:
        with st.spinner("Generating response..."):
            reply = gemini_chat(user_text)
        st.markdown(f"**Bot says:** {reply}")

        with st.spinner("Speaking..."):
            speak_text_to_wav(reply, WAV_OUT)

        embed_autoplay_audio(WAV_OUT)
