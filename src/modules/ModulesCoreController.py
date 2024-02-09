import logging
import re
from datetime import datetime

import requests
import os
from pprint import pprint

import sqlalchemy
from abc import ABC, abstractmethod
import openai
from config import OpenAIConfig


class ModulesCoreController(ABC):
    def __init__(self):
        """
        The constructor of the class. Initializes the logger for this class.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.setup_logging()


    def setup_logging(self):
        """
        Sets up the logging for this class. Creates a time-based rotating log file in specified directory.
        """

        # Ensure log directory exists
        if not os.path.exists('log'):
            os.makedirs('log')

        # Create a timed rotating file handler
        # USe the current date in the filename
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_filename = os.path.join('log', f'application_{date_str}.log')
        fh = logging.FileHandler(log_filename)
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
        This method is used to return a SQLAlchemy null value.

        Often, this is necessary when you want to set a database field to NULL. By default, SQLAlchemy considers
        NULL as the absence of a value. This method, therefore, can be used to explicitly remove any existing value
        for a certain database field, thus setting it to NULL.

        It does not take any parameters and does not modify any object states. It simply returns a special value that
        represents NULL in SQLAlchemy's database abstraction layer.

        :return: sqlalchemy.null()
        """

        # The method returns a special constant that SQLAlchemy uses to represent NULL
        return sqlalchemy.null()


    """ APIs """

    # Countries
    def api_get_country_by_ccn3(self, ccn3, filter_list=None):
        """
        Retrieves country information from the Rest Countries API using the CCN3 code.

        Args:
            ccn3 (str): The CCN3 code of the country (e.g., '276' for Germany).

        Returns:
            dict: A dictionary containing country information if successful, None otherwise.

        Raises:
            requests.exceptions.RequestException: An error occurred during the API request.
        """
        if len(ccn3) != 3:
            self.logger.error("CCN3 needs to be 3 characters long. Given CCN3: %s", ccn3)
            return None
        try:
            # Constructing the API URL
            url = f"https://restcountries.com/v3.1/alpha?codes={ccn3}"
            if filter_list:
                url = url + "&fields="
                for filter in filter_list:
                    url = url + filter + ','

            # Making the GET request to the API
            response = requests.get(url)

            # Raise an exception if the request was unsuccessful
            response.raise_for_status()

            # Parsing the JSON response
            country_data = response.json()

            # Return the country information
            return country_data
        except requests.exceptions.RequestException as e:
            # Print the error and return None if an exception occurs
            print(f"An error occurred: {e}")
            return None

    """  AI - ChatGPT """

    def count_tokens(self, text):
        """
        Counts the number of tokens in a given text.
        A token is defined as a word, a number, or a punctuation mark.
        This is usefull for calculating the price for AI

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

    """ Abstract MEthods """

    @abstractmethod
    def sync_all_to_bridge(self):
        pass

    @abstractmethod
    def sync_all_from_bridge(self, bridge_entities):
        pass

    @abstractmethod
    def sync_one_to_bridge(self):
        pass

    @abstractmethod
    def sync_one_from_bridge(self, bridge_entity):
        pass

    @abstractmethod
    def sync_changed_to_bridge(self):
        pass

    @abstractmethod
    def sync_changed_from_bridge(self, bridge_entities):
        pass
