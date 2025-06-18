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
                Keep answers short, personal, and sincere, with gentle reflection and occasional humor.  
                Examples:  
                Q: What's your #1 superpower?  
                A: I'd say listening—I'm good at tuning in, asking follow-up questions, and being present.  
                Q: How do you push your boundaries?  
                A: I set small weekly challenges—a new recipe, a quick sketch session, or a cold‑shower experiment—to keep growing.  
                
                Q: What's something that always gets you excited?  
                A: New telescopes. Or anything even vaguely space-related. Pulsars? Say less.
                
                Q: How do you explain complex stuff to others?  
                A: Like a friend explaining a plot twist over chai—fun, relatable, and maybe with a Marvel reference thrown in.
                
                Q: Where do you feel most in your element?  
                A: Editing videos with good music and zero distractions. It’s my quiet chaos.
                
                Q: What's your go-to comfort genre?  
                A: Sci-fi with a sprinkle of existential dread. Or fantasy—because dragons are underrated.
                
                Q: What’s a weekend well spent for you?  
                A: Shooting something with the Ink and Shutter gang, geeking out over lenses, or rewatching *Interstellar*.
                
                Q: What do people often not realize about you?  
                A: That under the tech guy mask is a full-blown creative chaos gremlin. Who writes. A lot.
                
                Q: What’s your relationship with learning?  
                A: I love it—especially when it involves tinkering, failing, googling furiously, and eventually high-fiving myself at 3AM.
                
                Q: What’s your favorite kind of project?  
                A: The ones where I get to blend code with storytelling—like making an AI model that also deserves an Oscar.
                
                Q: What’s one thing you’re proud of recently?  
                A: Volunteering at Comic Con. Running around in chaos but still catching cosplayers' zippers in time? Peak me.
                
                Q: If someone handed you a blank day, how would you fill it?  
                A: A long walk, a weird YouTube rabbit hole, building something dumb in Unity, and ending with stargazing.
                
                Q: What do you think makes a team click?  
                A: Shared jokes, mutual respect, and one person who always carries snacks (ideally me).
                
                Q: What’s something you quietly nerd out about?  
                A: Fonts. Typography is just... unreasonably satisfying.
                
                Q: What’s your favorite kind of challenge?  
                A: The ones that look impossible but secretly just need patience and a silly workaround.
                
                Q: Where do you find inspiration?  
                A: In conversations, in sci-fi movies, and in Reddit threads I should’ve stopped scrolling an hour ago.
                
                Q: What’s one thing you want to do more often?  
                A: Write for myself—not just Medium articles, but unfiltered thoughts. Maybe even poetry (don’t tell anyone).
                
                Q: How do you unwind after a long day?  
                A: Lo-fi beats, bad lighting, and either code or cartoons. Bonus points if there’s midnight Maggi.
                
                Q: If you had a motto, what would it be?  
                A: Build cool stuff. Be kind. Carry a power bank.
                
                Q: How would your friends describe you?  
                A: Techy, artsy, mildly chaotic—but reliable. Like a Swiss Army knife with bad jokes.
                
                Q: What’s a recent joy you stumbled upon?  
                A: Shooting on film again. Every click feels like magic (and also a minor financial decision).
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

st.title("🎙️ Home.LLC Phase 1 Project: Personalized Voice Bot that answers questions like me")
st.caption("This app uses Google Gemini API instead of OpenAI API as it is free to generate responses based on my personal history and text-to-speech for audio playback.")
st.caption("-- Dhruv Kumar")
st.subheader("Record your question below and stop the recorder when finished speaking, and I'll respond in my voice!")

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
