import logging
import re
from logging.handlers import TimedRotatingFileHandler
import os
from pprint import pprint

import sqlalchemy
from abc import ABC, abstractmethod
import openai
from config import OpenAIConfig


class ModulesCoreController(ABC):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logging()

    def setup_logging(self):
        # Set the logging level
        self.logger.setLevel(logging.DEBUG)

        # Ensure log directory exists
        if not os.path.exists('log'):
            os.makedirs('log')

        # Create a timed rotating file handler
        # The 'midnight' argument means the log will rotate at midnight
        log_filename = os.path.join('log', 'application.log')
        fh = TimedRotatingFileHandler(log_filename, when='midnight', interval=1, backupCount=7)  # backupCount keeps the last 7 logs
        fh.setLevel(logging.DEBUG)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s.%(funcName)s - %(levelname)s - %(message)s')

        # Add formatter to the handler
        fh.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(fh)

    # SQL Alchemy Method
    def set_null(self):
        """
        When sending none to a field, the string none is set.
        We need the actual NONE to set the field to NULL
        """
        return sqlalchemy.null()

    # AI - ChatGPT
    def count_tokens(self, text):
        """
        Counts the number of tokens in a given text.

        A token is defined as a word, a number, or a punctuation mark.

        :param text: The text to tokenize.
        :type text: str
        :return: The number of tokens in the text.
        :rtype: int
        """
        # Regular expression pattern to match words, numbers, or punctuation marks
        pattern = re.compile(r'\w+|\S')
        tokens = re.findall(pattern, text)
        return len(tokens)

    def ai_translate_to(self,text:str, language="GB_en"):
        """
        Sends a prompt to GPT-3.5 and returns the generated response.

        :param prompt: The prompt to send to GPT-3.5.
        :type prompt: str
        :return: The generated response from GPT-3.5.
        :rtype: str
        """
        # Set up the OpenAI API client with your API key
        if not text:
            return
        openai.api_key = OpenAIConfig.API_KEY

        try:
            # Send the prompt to GPT-3.5
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"Translate to {language}. Keep the html markup. No elaboration, just translate."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                max_tokens=1000  # You can adjust the max tokens as needed
            )
            # Extract and return the generated text from the response
            generated_text = response['choices'][0]['message']['content']
            pprint(response)
            return generated_text
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    @abstractmethod
    def sync_all_to_bridge(self):
        pass

    @abstractmethod
    def sync_all_from_bridge(self):
        pass

    @abstractmethod
    def sync_one_to_bridge(self):
        pass

    @abstractmethod
    def sync_one_from_bridge(self):
        pass

    @abstractmethod
    def sync_changed_to_bridge(self):
        pass

    @abstractmethod
    def sync_changed_from_bridge(self):
        pass