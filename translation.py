from dotenv import load_dotenv
import os
import azure.cognitiveservices.speech as speech_sdk
from googletrans import Translator

def load_speech_config():
    """Load Azure Speech SDK configuration from environment variables."""
    load_dotenv()
    ai_key = os.getenv('SPEECH_KEY')
    ai_region = os.getenv('SPEECH_REGION')

    if not ai_key or not ai_region:
        raise ValueError("Missing SPEECH_KEY or SPEECH_REGION in environment variables.")

    speech_config = speech_sdk.SpeechConfig(subscription=ai_key, region=ai_region)
    return speech_config


def translate_text(text, target_language):
    """
    Translate the input text into the target language using Google Translate.
    """
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        return f"Error in translation: {e}"


def recognize_speech():
    """
    Recognize speech input using Azure Cognitive Services.
    """
    try:
        speech_config = load_speech_config()
        audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
        recognizer = speech_sdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        print("Listening... (Say 'quit' to exit speak mode)")
        result = recognizer.recognize_once_async().get()

        if result.reason == speech_sdk.ResultReason.RecognizedSpeech:
            return result.text.strip(".!?\n ")
        elif result.reason == speech_sdk.ResultReason.NoMatch:
            print("No speech recognized. Please try again.")
            return None
        else:
            print(f"Speech recognition error: {result.reason}")
            return None
    except Exception as e:
        print(f"Error recognizing speech: {e}")
        return None


def text_to_speech(text, language_code="en"):
    """
    Synthesize speech from text using Azure Cognitive Services.
    """
    try:
        speech_config = load_speech_config()
        voices = {
            "en": "en-US-AriaNeural",
            "fr": "fr-FR-HenriNeural",
            "es": "es-ES-ElviraNeural",
            "hi": "hi-IN-MadhurNeural",
            "ja": "ja-JP-NanamiNeural",
            "ko": "ko-KR-SunHiNeural",
        }

        if language_code in voices:
            speech_config.speech_synthesis_voice_name = voices[language_code]
        else:
            speech_config.speech_synthesis_voice_name = voices["en"]

        synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
        synthesizer.speak_text_async(text).get()

    except Exception as e:
        print(f"Error in text-to-speech synthesis: {e}")


def run_translation_tool():
    """
    A standalone function to translate speech-to-speech between languages.
    """
    try:
        speech_config = load_speech_config()

        # Configure translation
        translation_config = speech_sdk.translation.SpeechTranslationConfig(
            subscription=speech_config.subscription_key, region=speech_config.region
        )
        translation_config.speech_recognition_language = "en-US"
        translation_config.add_target_language("fr")
        translation_config.add_target_language("es")
        translation_config.add_target_language("hi")
        translation_config.add_target_language("ja")
        translation_config.add_target_language("ko")

        # Configure audio input
        audio_config = speech_sdk.AudioConfig(use_default_microphone=True)
        translator = speech_sdk.translation.TranslationRecognizer(translation_config, audio_config=audio_config)

        print("Ready to translate. Speak now... (Say 'quit' to exit)")
        while True:
            result = translator.recognize_once_async().get()

            if result.reason == speech_sdk.ResultReason.TranslatedSpeech:
                print(f"Original: {result.text}")
                for lang, translation in result.translations.items():
                    print(f"Translated ({lang}): {translation}")
                    text_to_speech(translation, lang)
            elif result.reason == speech_sdk.ResultReason.RecognizedSpeech:
                print(f"Recognized: {result.text}")
            elif result.reason == speech_sdk.ResultReason.NoMatch:
                print("No speech recognized. Please try again.")
            else:
                print(f"Speech recognition error: {result.reason}")

    except Exception as e:
        print(f"An error occurred: {e}")