from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from translate import Translator
from gtts import gTTS

import os
import re


class Interface:
    """ Creates a bilingual interface to a locally installed Ollama2 large language model (LLM). """

    def __init__(self, language: str):
        """ Initialise the interface (English-to-language and language-to-English translators and the LLM).
        :param language: a 2-letter language code (lowercase), specifies the second (non-English) language.
        """

        # initialise two-way translators
        self._language = language
        self._en_to_lang = Translator(from_lang='en', to_lang=language)
        self._lang_to_en = Translator(from_lang=language, to_lang='en')

        # create the LLM interface with a locally installed Ollama2 model
        self._llm = Ollama(model='llama2')
        self._prompt = ChatPromptTemplate.from_messages([
            ('system', 'You work in a {context}. Answer questions in beginner English in one very short sentence.'),
            ('user', '{input}')
        ])
        self._chain = self._prompt | self._llm

    def get_response(self, context: str, query: str) -> (str, str):
        """
        Creates a text reply in two languages.
        Generates and saves a voice in the non-English language into a file called 'voice.mp3'.
        :param context:  the setting in which the speaker is placed
        :param query:    the information that needs to be generated
        :return:         (English, [Language]) string tuple.
        """

        # remove old voice files
        if os.path.exists('voice.mp3'):
            os.remove('voice.mp3')

        # generate an English response using the LLM
        # strip the response of non-verbal elements the LLM sometimes creates
        response = re.sub(r' \*.*?\*', '',
                          self._chain.invoke({'input': query, 'context': context}))

        # pass through the translator to second language then back to English to improve syntax
        lang_text = self._en_to_lang.translate(response)
        en_text = self._lang_to_en.translate(lang_text)

        # generate text-to-speech sound file
        speech = gTTS(lang_text, lang=self._language)
        speech.save('voice.mp3')

        return en_text, lang_text
