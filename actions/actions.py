# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class DafaultFallbackAction(Action):

    def name(self) -> Text:
        return "action_fallback"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="PASS")

        return []




from cq_code_builder import CqCodeBuilder

import requests
import os
import random


DATA_DIR = r'D:\Code\MyLongTimeProject\A\QQ-Bot-And-Tool\data'
cqCodeBuilder = CqCodeBuilder("http://localhost:8882/",os.path.join(DATA_DIR,'images'))

SETU_TAG = ['黑丝','兽耳','萝莉','巨乳','贫乳','爱丽丝']

class GetSetuAction(Action):

    def name(self) -> Text:
        return "action_get_setu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message_text = tracker.latest_message['text']
        print( "action_get_setu")
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

