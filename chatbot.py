from dotenv import load_dotenv
import os
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
    recognizer = speech_sdk.SpeechRecognizer(speech_config=speech_config)
    synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
    return recognizer, synthesizer


# Initialize Hugging Face model
qa_pipeline = pipeline("text2text-generation", model="google/flan-t5-base")


def get_faq_response(question):
    """
    Generate a response to the question using Hugging Face model.
    """
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
    recognizer, synthesizer = initialize_speech_services(config)

    voices = {
        "en": ("en-US-AriaNeural", "English"),
        "hi": ("hi-IN-MadhurNeural", "Hindi"),
        "mr": ("mr-IN-AarohiNeural",     "Marathi"),
        "fr": ("fr-FR-HenriNeural", "French"),
        "es": ("es-ES-ElviraNeural", "Spanish"),
        "ja": ("ja-JP-NanamiNeural", "Japanese"),
        "ko": ("ko-KR-SunHiNeural", "Korean")
    }

    print("Welcome to the Customer Care Chatbot!")
    print("You can either speak or type your question. Type or say 'quit' to exit.")

    preferred_language = "en"  # Default language is English

    mode = None
    while True:
        if not mode:
            mode = input("Would you like to speak or write your question? (Type 'speak' or 'write'): ").strip().lower()

            if mode == "quit":
                print("Chatbot: Goodbye!")
                synthesizer.speak_text_async("Thank you! Have a nice day!").get()
                break

            if mode == "speak":
                # Ask for language selection in speak mode
                print("Available languages: en (English), hi (Hindi), mr (Marathi), fr (French), es (Spanish)")
                language_input = input("Select your preferred language code for responses: ").strip().lower()
                if language_input in voices:
                    preferred_language = language_input
                    language_name = voices[language_input][1]
                    print(f"Language set to {language_name} ({language_input})")
                    synthesizer.speak_text_async(f"Language set to {language_name}.").get()
                else:
                    print("Invalid language code. Defaulting to English.")
                    preferred_language = "en"

            if mode not in ["speak", "write"]:
                print("Invalid choice. Please type 'speak' or 'write'.")
                mode = None
                continue

        if mode == "speak":
            user_text = recognize_speech(recognizer)
            if user_text is None:
                continue
            if user_text.lower() == "quit":  # Exit the program if "Quit" is spoken
                print("Exiting chatbot. Goodbye!")
                synthesizer.speak_text_async("Goodbye! Thank you for using the chatbot.").get()
                exit()  # Terminate the program immediately
            print(f"You said: {user_text}")

        elif mode == "write":
            user_text = input("You: ").strip(".!?\n ")
            if user_text.lower() == "quit":  # Case-insensitive check for 'quit'
                print("Chatbot: Goodbye!")
                synthesizer.speak_text_async("Thank you! Have a nice day!").get()
                break
            print(f"You wrote: {user_text}")

        # Check for greetings and respond with real-time greeting
        if user_text.lower() in ["good morning", "good afternoon", "good evening", "hello", "hi"]:
            greeting_response = get_real_time_greeting()

            # Translate the greeting to the preferred language if necessary
            if preferred_language != "en":
                greeting_response = translate_text(greeting_response, preferred_language)

            print(f"Chatbot: {greeting_response}")
            speech_config = speech_sdk.SpeechConfig(subscription=config['speech_key'], region=config['speech_region'])
            speech_config.speech_synthesis_voice_name = voices[preferred_language][0]
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

        # Translate the response if the preferred language is not English
        if preferred_language != "en":
            response = translate_text(response, preferred_language)

        # Speak the response in the preferred language
        if preferred_language in voices:
            speech_config = speech_sdk.SpeechConfig(subscription=config['speech_key'], region=config['speech_region'])
            speech_config.speech_synthesis_voice_name = voices[preferred_language][0]

            localized_synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
            localized_synthesizer.speak_text_async(response).get()
            print(f"Chatbot Response ({voices[preferred_language][1]}): {response}")
        else:
            print(f"Chatbot: {response}")

    print("Chatbot session ended.")


if __name__ == "_main_":
    config = load_environment_variables()
    chatbot_interaction(config)