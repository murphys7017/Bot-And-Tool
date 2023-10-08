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
from service.cq_code_builder import CqCodeBuilder
from service.utils import get_weather_abstract_by_hefeng, get_ghs_picture

from service import config




class DafaultFallbackAction(Action):

    def name(self) -> Text:
        return "action_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="PASS")

        return []


SETU_TAG = ['黑丝','兽耳','萝莉','巨乳','贫乳','爱丽丝']
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
      
    
        dispatcher.utter_message(get_ghs_picture(tags))

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
            dispatcher.utter_message(get_weather_abstract_by_hefeng(address))
        return []

class GetWifiByRandom(Action):
    def name(self) -> Text:
        """Unique identifier of the form"""

        return "action_get_wifi_by_random"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        dispatcher.utter_message("RASA_RUN_FUNCTION_By_COMMAND:")
        return []