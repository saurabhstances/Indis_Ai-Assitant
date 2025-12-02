import speech_recognition as sr
from gtts import gTTS
import pygame
import pywhatkit
import google.generativeai as genai
import webbrowser
import datetime
import pyautogui
import os
import time
from AppOpener import open as app_open
from dotenv import load_dotenv
import pyaudio

# --- GLOBAL CONFIG ---
INPUT_MODE = "voice" # Default to voice

# --- NEW FUNCTION: FILE SCANNER ---
def find_and_open(filename):
    speak(f"Scanning for {filename}...", lang='en')
    user_path = os.path.expanduser("~")
    search_dirs = [
        os.path.join(user_path, "Desktop"),
        os.path.join(user_path, "Documents"),
        os.path.join(user_path, "Downloads"),
        os.path.join(user_path, "Music"),
        os.path.join(user_path, "Videos"),
        os.path.join(user_path, "Pictures")
    ]
    for folder in search_dirs:
        for root, dirs, files in os.walk(folder):
            for file in files:
                if filename.lower() in file.lower():
                    full_path = os.path.join(root, file)
                    speak(f"Found it. Opening {file}", lang='en')
                    try:
                        os.startfile(full_path)
                    except Exception as e:
                        speak(f"Error opening file: {e}", lang='en')
                    return True
    speak("Sorry Sir, file not found.", lang='en')
    return False

# --- 1. CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    API_KEY = "AIzaSyDNOFJRsvGx_InqKTJzhk7S1phiRItqlHw" # Backup Key

genai.configure(api_key=API_KEY)

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel('gemini-2.0-flash', safety_settings=safety_settings)
chat_session = model.start_chat(history=[
    {"role": "user", "parts": ["You are INDIS. Be helpful. If asked in Hindi, answer in Hindi. Keep answers short."]},
    {"role": "model", "parts": ["Understood Sir."]}
])

# --- 2. AUDIO ENGINE ---
pygame.mixer.init()

def speak(text, lang='en'):
    print(f"INDIS: {text}")
    clean_text = text.replace("*", "").replace("#", "")
    
    if os.path.exists("voice.mp3"):
        try:
            os.remove("voice.mp3")
        except:
            return 
    
    try:
        if lang == 'hi':
            tts = gTTS(text=clean_text, lang='hi', slow=False)
        else:
            tts = gTTS(text=clean_text, lang='en', tld='co.in', slow=False)
            
        tts.save("voice.mp3")
        pygame.mixer.music.load("voice.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"Audio Error: {e}")

# --- UPDATED INPUT FUNCTION (TEXT + VOICE) ---
def take_command():
    # If Text Mode is selected, just ask for input
    if INPUT_MODE == "text":
        return input("\nYOU: ").lower()

    # If Voice Mode is selected, listen to Mic
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening...")
        r.adjust_for_ambient_noise(source)
        try:
            audio = r.listen(source, timeout=5)
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User (Voice): {query}")
        except:
            return "none"
    return query.lower()

# --- 3. MAIN SYSTEM ---
if __name__ == "__main__":
    
    # --- SELECT MODE AT START ---
    print("-----------------------------")
    print("1. Voice Mode (Speak)")
    print("2. Text Mode (Type)")
    print("-----------------------------")
    choice = input("Select Mode (1 or 2): ")
    
    if choice == "2":
        INPUT_MODE = "text"
        speak("Text Mode Activated. Please type your commands.", lang='en')
    else:
        INPUT_MODE = "voice"
        speak("Voice Mode Activated. I am listening.", lang='en')

    while True:
        query = take_command()
        
        if query == "none" or query == "":
            continue

        # --- A. TASKS ---
        if 'play' in query:
            song = query.replace('play', '').strip()
            speak(f"Playing {song}.")
            pywhatkit.playonyt(song) 

        elif 'open' in query and 'website' in query:
            site = query.replace('open', '').replace('website', '').strip()
            speak(f"Opening {site}.")
            webbrowser.open(f"https://www.{site}.com")

        elif 'time' in query:
            strTime = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"It is {strTime}.")

        elif 'screenshot' in query:
            speak("Taking screenshot.")
            pyautogui.screenshot('ss.png')
            speak("Done.")

        # --- GOOGLE SEARCH ---
        elif 'search' in query:
            topic = query.replace('search', '').strip()
            speak(f"Searching Google for {topic}")
            pywhatkit.search(topic)

        elif 'quit' in query or 'bye' in query:
            speak("Goodbye Sir.")
            break

        # --- FILE / APP OPENER ---
        elif 'open' in query:
            target = query.replace('open', '').replace('file', '').strip()
            if target == "": continue

            speak(f"Looking for {target}...")
            try:
                app_open(target, match_closest=True, throw_error=True)
                speak(f"Opened {target} App.")
            except:
                find_and_open(target)

        # --- AI BRAIN ---
        else:
            try:
                if "in hindi" in query or "hindi mein" in query:
                    response = chat_session.send_message(f"{query}. (Answer in Hindi)")
                    speak(response.text, lang='hi')
                else:
                    response = chat_session.send_message(query)
                    speak(response.text, lang='en')
            except Exception as e:
                print(e)
                speak("Connection Error.")