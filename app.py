import streamlit as st
from dotenv import load_dotenv
import os
import azure.cognitiveservices.speech as speech_sdk
from transformers import pipeline
from translation import translate_text  # Ensure translation.py is included in your project

def load_environment_variables():
    """Load environment variables from .env file."""
    load_dotenv()
    return {
        "speech_key": os.getenv("SPEECH_KEY"),
        "speech_region": os.getenv("SPEECH_REGION"),
    }

def get_faq_response(question):
    """Match the user's question with the FAQ database and return an answer."""
    faq_database = {
        # English FAQs
        "what is your return policy": "Our return policy allows returns within 30 days of purchase.",
        "how can i track my order": "You can track your order through the 'My Orders' section on our website.",
        "what payment methods do you accept": "We accept credit/debit cards, PayPal, and other online payment options.",
        "do you offer international shipping": "Yes, we offer international shipping to select countries.",
        "how do i cancel my order": "To cancel your order, go to 'My Orders' and select 'Cancel Order'.",
        "how long does shipping take": "Shipping typically takes 5-7 business days.",
        "can i change my order after placing it": "You can change your order within one hour of placing it.",
        "do you have a loyalty program": "Yes, we have a loyalty program that rewards you for every purchase.",
        "how do i contact customer service": "You can contact customer service via email or phone.",
        "what should i do if i receive a damaged item": "Please contact us immediately for a replacement or refund.",
        "is there a warranty on products": "Yes, most products come with a one-year warranty.",
        "how can i leave feedback about my experience": "You can leave feedback through our website's feedback form.",
        "do you offer gift cards": "Yes, we offer gift cards that can be purchased online.",
        "can i pick up my order in-store": "Yes, in-store pickup is available for select items.",
        "what if i forgot my password": "You can reset your password using the 'Forgot Password' link on the login page.",
        "are there any discounts available right now": "Check our website for current promotions and discounts.",
        "how can i update my address": "You can update your address through the 'My Account' section of our website.",
        "what should i do if i didn’t receive my order": "If your order hasn’t arrived, please contact customer service for assistance.",
        "how do i report a problem with my order": "Please contact customer service to report any issues with your order.",
        "can i speak to a customer care agent": "Yes, you can contact our customer care team via phone, email, or live chat.",

        # Simple Gesture Questions
        "hello": "Hi there! How can I assist you today?",
        "good morning": "Good morning! I hope you have a wonderful day ahead. How can I help you?",
        "good evening": "Good evening! How was your day? Let me know how I can assist you.",
        "how are you": "I'm just a program, but I'm here and ready to help you!",
        "what's your name": "I'm your friendly AI assistant, here to make your life easier.",
        "what can you do": "I can answer your questions, translate languages, and assist you with various tasks.",
        "thank you": "You're welcome! Let me know if there's anything else I can help with.",
        "who are you": "I am an AI chatbot designed to assist you with your queries and provide support.",
        "tell me a joke": "Why don’t skeletons fight each other? Because they don’t have the guts!",
        "how is the weather": "I'm not sure, but you can check the weather app for accurate updates."
    }

    # Normalize input question
    normalized_question = question.lower().strip()

    # Check for direct match
    if normalized_question in faq_database:
        return faq_database[normalized_question]

    # Fallback: Check for similar questions
    for key in faq_database.keys():
        if key in normalized_question or normalized_question in key:
            return faq_database[key]

    return "I'm sorry, I don't have an answer for that question."

# Load environment variables
config = load_environment_variables()

# Configure Azure Speech Services
speech_config = speech_sdk.SpeechConfig(subscription=config['speech_key'], region=config['speech_region'])
synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
recognizer = speech_sdk.SpeechRecognizer(speech_config=speech_config)

def synthesize_response(response, language_code):
    """Synthesize speech response in the selected language."""
    voices = {
        'en': 'en-US-AriaNeural',      # English
        'hi': 'hi-IN-MadhurNeural',    # Hindi
        'mr': 'mr-IN-AarohiNeural',    # Marathi
        'es': 'es-ES-ElviraNeural',    # Spanish
        'fr': 'fr-FR-HenriNeural',     # French
        'ja': 'ja-JP-NanamiNeural'     # Japanese
    }
    
    if language_code in voices:
        speech_config.speech_synthesis_voice_name = voices[language_code]
        localized_synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
        localized_synthesizer.speak_text_async(response).get()

def recognize_speech():
    """Recognize speech input and handle errors."""
    result = recognizer.recognize_once_async().get()
    if result.reason == speech_sdk.ResultReason.RecognizedSpeech:
        return result.text.strip()
    elif result.reason == speech_sdk.ResultReason.NoMatch:
        st.error("No speech recognized. Please try again.")
    else:
        st.error(f"Speech recognition error: {result.reason}")
    return None

st.title("Multilingual Customer Care Chatbot")
st.write("Welcome! Ask your questions by typing or speaking them below. You can also switch languages.")

# Language selection
language_code = st.selectbox("Select your preferred language:", ["en", "hi", "mr", "fr", "es", 'ja'], format_func=lambda x: {
    'en': 'English',
    'hi': 'Hindi',
    'mr': 'Marathi',
    'es': 'Spanish',
    'fr': 'French',
    'ja': 'Japanese'
}[x])

# Input mode selection
input_mode = st.radio("Choose your input method:", ("Type", "Speak"))

user_text = ""
if input_mode == "Type":
    user_text = st.text_input("Type your question here:")
elif input_mode == "Speak":
    if st.button("Start Speaking"):
        st.info("Listening...")
        user_text = recognize_speech()

if user_text:
    st.write(f"You said: {user_text}")
    
    with st.spinner('Generating response...'):
        response = get_faq_response(user_text)

        if response:
            # Translate if necessary
            if language_code != 'en':
                response = translate_text(response, language_code)

            st.success(f"Chatbot: {response}")
            synthesize_response(response, language_code)
        else:
            st.error("Unable to generate a response. Please try rephrasing your question.")