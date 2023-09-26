# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import requests
import os
import random
from bs4 import BeautifulSoup

from cq_code_builder import CqCodeBuilder

HF_USER_KEY = '4fd5b28a9a27428e92dd14cada996806'
DATA_DIR = r'D:\Code\MyLongTimeProject\A\QQ-Bot-And-Tool\data'
cqCodeBuilder = CqCodeBuilder("http://localhost:8882/",os.path.join(DATA_DIR,'images'))

SETU_TAG = ['黑丝','兽耳','萝莉','巨乳','贫乳','爱丽丝']


class DafaultFallbackAction(Action):

    def name(self) -> Text:
        return "action_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="PASS")

        return []


class GetSetuAction(Action):

    def name(self) -> Text:
        return "action_get_setu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message_text = tracker.latest_message['text']
        
        tags = []
        for tag in SETU_TAG:
            if tag in message_text:
                tags.append(tag)
        if len(tags) > 0:
            params = {
                        'r18':0,
                        'num': 1,
                        'tag': tags
                    }
            response = requests.get('https://api.lolicon.app/setu/v2', params=params).json()['data'][0]['urls']['original']
            dispatcher.utter_message(text=cqCodeBuilder.imageDoCache(response))
        else:
            local_path = os.path.join(os.path.join(DATA_DIR,'images'))
            dispatcher.utter_message(cqCodeBuilder.image(os.path.join(local_path, random.sample(os.listdir(local_path),1)[0])))

        return []



class WeatherForm(Action):

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "action_weather_form"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        address = tracker.get_slot('address')
        if len(address) > 1:
            

            get_location_url = 'https://geoapi.qweather.com/v2/city/lookup'
            get_loction_params = {
                'key': HF_USER_KEY,
                'location': address
            }
            location_data = requests.get(get_location_url,get_loction_params).json()['location'][0]
            page = requests.get(location_data['fxLink'])
            soup = BeautifulSoup(page.text, 'html.parser')
            abstract = soup.find_all('div', class_='current-abstract')[0]
            dispatcher.utter_message(abstract.text.strip() + '\n 详细信息：'+location_data['fxLink'])
        return []