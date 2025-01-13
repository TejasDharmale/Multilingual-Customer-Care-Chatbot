from dotenv import load_dotenv
import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speech_sdk
from transformers import pipeline
from translation import translate_text  # Import the translation function from translation.py
from datetime import datetime  # Import datetime for real-time greetings

def load_environment_variables():
    """Load environment variables from .env file."""
    load_dotenv()
    return {
        "speech_key": os.getenv("SPEECH_KEY"),
        "speech_region": os.getenv("SPEECH_REGION"),
    }

def initialize_speech_services(config):
    """Initialize speech recognizer and synthesizer."""
    speech_config = speech_sdk.SpeechConfig(subscription=config['speech_key'], region=config['speech_region'])
    synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
    recognizer = speech_sdk.SpeechRecognizer(speech_config=speech_config)
    return recognizer, synthesizer, speech_config

# Initialize Hugging Face model
qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")

def get_faq_response(question):
    """
    Generate a response to the question using predefined FAQs or Hugging Face model.
    """
    faq_database = {
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

    normalized_question = question.lower().strip()
    response = faq_database.get(normalized_question)

    if response:
        return response

    try:
        response = qa_pipeline(question, max_length=150, do_sample=False)
        return response[0]['generated_text']
    except Exception as e:
        print(f"Error with Hugging Face model: {e}")
        return None

def recognize_speech(recognizer):
    """Recognize speech input and handle errors."""
    print("Listening... (Say 'quit' to exit chatbot)")
    result = recognizer.recognize_once_async().get()
    if result.reason == speech_sdk.ResultReason.RecognizedSpeech:
        return result.text.strip(".!?\n ")
    elif result.reason == speech_sdk.ResultReason.NoMatch:
        print("No speech recognized. Please try again.")
        return None
    else:
        print(f"Speech recognition error: {result.reason}")
        return None

def get_real_time_greeting():
    """Get a greeting based on the current time."""
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Good morning! How can I assist you?"
    elif 12 <= current_hour < 18:
        return "Good afternoon! How can I assist you?"
    else:
        return "Good evening! How can I assist you?"

def chatbot_interaction(config):
    """Main interaction loop for the chatbot."""
    recognizer, synthesizer, speech_config = initialize_speech_services(config)

    voices = {
        "en": ("en-US-AriaNeural", "English"),
        "hi": ("hi-IN-MadhurNeural", "Hindi"),
        "mr": ("mr-IN-AarohiNeural", "Marathi"),
        "fr": ("fr-FR-HenriNeural", "French"),
        "es": ("es-ES-ElviraNeural", "Spanish"),
        "ja": ("ja-JP-NanamiNeural", "Japanese"),
        "ko": ("ko-KR-SunHiNeural", "Korean")
    }

    print("Welcome to the Customer Care Chatbot!")
    print("You can either speak or type your question. Type or say 'quit' to exit.")

    preferred_language = "en"  # Default language is English
    speech_config.speech_synthesis_voice_name = voices[preferred_language][0]
    volume = 75  # Default volume level

    mode = None
    while True:
        if not mode:
            mode = input("Would you like to speak or write your question? (Type 'speak' or 'write'): ").strip().lower()

            if mode == "quit":
                print("Chatbot: Goodbye!")
                synthesizer.speak_text_async("Thank you! Have a nice day!").get()
                break

            if mode == "speak":
                print("Available languages: en (English), hi (Hindi), mr (Marathi), fr (French), es (Spanish)")
                language_input = input("Select your preferred language code for responses: ").strip().lower()
                if language_input in voices:
                    preferred_language = language_input
                    language_name = voices[language_input][1]
                    print(f"Language set to {language_name} ({language_input})")
                    synthesizer.speak_text_async(f"Language set to {language_name}.").get()
                    speech_config.speech_synthesis_voice_name = voices[preferred_language][0]
                else:
                    print("Invalid language code. Defaulting to English.")
                    preferred_language = "en"

            if mode not in ["speak", "write"]:
                print("Invalid choice. Please type 'speak' or 'write'.")
                mode = None
                continue

        # Volume adjustment option
        adjust_volume = input("Would you like to adjust the volume? (Type 'yes' to adjust, 'no' to continue): ").strip().lower()
        if adjust_volume == "yes":
            try:
                volume = int(input("Set the volume level (0-100, default is 75): ").strip())
                volume = max(0, min(100, volume))  # Ensure volume is within valid range
                speech_config.speech_synthesis_volume = volume
                print(f"Volume set to {volume}.")
            except ValueError:
                print("Invalid input. Volume remains unchanged.")

        if mode == "speak":
            user_text = recognize_speech(recognizer)
            if user_text is None:
                continue
            if user_text.lower() == "quit":
                print("Exiting chatbot. Goodbye!")
                synthesizer.speak_text_async("Goodbye! Thank you for using the chatbot.").get()
                exit()
            print(f"You said: {user_text}")

        elif mode == "write":
            user_text = input("You: ").strip(".!?\n ")
            if user_text.lower() == "quit":
                print("Chatbot: Goodbye!")
                synthesizer.speak_text_async("Thank you! Have a nice day!").get()
                break
            print(f"You wrote: {user_text}")

        # Check for greetings and respond with real-time greeting
        if user_text.lower() in ["good morning", "good afternoon", "good evening", "hello", "hi"]:
            greeting_response = get_real_time_greeting()

            if preferred_language != "en":
                greeting_response = translate_text(greeting_response, preferred_language)

            print(f"Chatbot: {greeting_response}")
            localized_synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
            localized_synthesizer.speak_text_async(greeting_response).get()
            continue

        # Get FAQ response
        response = get_faq_response(user_text)

        if not response:
            if mode == "speak":
                response = "That question seems incorrect. Please try rephrasing it."
                print(f"Chatbot: {response}")
                synthesizer.speak_text_async(response).get()
            elif mode == "write":
                response = "That question seems incorrect. Please correct it and try again."
                print(f"Chatbot: {response}")
            continue

        if preferred_language != "en":
            response = translate_text(response, preferred_language)

        localized_synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
        localized_synthesizer.speak_text_async(response).get()
        print(f"Chatbot Response ({voices[preferred_language][1]}): {response}")

    print("Chatbot session ended.")


if __name__ == "_main_":
    config = load_environment_variables()
    chatbot_interaction(config)
