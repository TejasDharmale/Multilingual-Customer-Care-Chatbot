# Multilingual Customer Care Chatbot

## Description

The **Multilingual Customer Care Chatbot** is an AI-powered system designed to provide seamless customer support in multiple languages. Built using Azure Cognitive Services and Python, the chatbot can interact with users via speech or text, detect their preferred language, and provide accurate responses based on a predefined FAQ database. It supports dynamic translation for non-English queries, ensuring a smooth and intuitive user experience.

---

## Features

- **Multilingual Support**: Handles queries in multiple languages, including English, Hindi, Marathi, Spanish, and French.
- **Speech and Text Interaction**: Users can ask questions via speech or text, and the chatbot responds accordingly.
- **Language Detection**: Automatically detects the user's language using Microsoft Azure Cognitive Services.
- **Dynamic Translation**: Translates the chatbot's responses into the user's preferred language for a personalized experience.
- **FAQ-Based Responses**: Answers customer queries based on a comprehensive and customizable FAQ database.
- **Available Questions Listing**: Allows users to request the list of all available questions in the FAQ database.

---

## Tech Stack

- **Programming Language**: Python
- **Cloud Services**: Azure Cognitive Services (Speech, Translation, and Language Detection)
- **Libraries**:
  - `azure.cognitiveservices.speech`
  - `requests`
  - `dotenv` (for environment variables)
- **Development Tools**: Visual Studio Code, Git

---

## How It Works

1. **Input Mode Selection**: Users choose between speech or text input.
2. **Language Detection**: The chatbot identifies the user's language via Azure's Language Service API.
3. **FAQ Query Handling**:
   - User queries are matched against a predefined FAQ database stored in `question.py`.
   - If the query matches, a response is returned in the user's language.
4. **Dynamic Translation**: If the detected language isn't English, responses are translated to the user's language using Azure's Translation API.
5. **Speech Synthesis**: The response is converted to speech using Azure Speech Services if the user prefers spoken output.
6. **Available Questions**: Users can ask, "What are the available questions?" to see the list of all FAQs.

---

## Prerequisites

1. **Azure Subscription**:
   - Azure Speech Service
   - Azure Language Detection Service
   - Azure Translation Service
2. **Environment Variables**:
   - `SPEECH_KEY`: Azure Speech API Key
   - `SPEECH_REGION`: Azure Speech API Region
   - `TRANSLATOR_KEY`: Azure Translation API Key
   - `TRANSLATOR_ENDPOINT`: Azure Translation API Endpoint
   - `LS_CONVERSATIONS_KEY`: Azure Language Detection API Key
   - `LS_CONVERSATIONS_ENDPOINT`: Azure Language Detection API Endpoint

3. **Python Packages**:
   Install required packages using:
   ```bash
   pip install -r requirements.txt
