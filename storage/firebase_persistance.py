from ast import literal_eval
from collections import defaultdict
from typing import Dict, List

from google.cloud import firestore
from google.cloud.firestore_v1 import DocumentSnapshot
from telegram.ext import BasePersistence
from telegram.ext.utils.types import UD


class FirebasePersistence(BasePersistence):
    def __init__(
            self,
            client,
            store_user_data=True,
            store_chat_data=True,
            store_bot_data=True,
    ):
        self.client = client
        self.fb_user_data = client.collection("user_data")
        self.fb_chat_data = client.collection("chat_data")
        self.fb_bot_data = defaultdict(dict, {})
        self.fb_conversations = client.collection("conversations")
        self.user_data = None
        self.chat_data = None
        super().__init__(
            store_user_data=store_user_data,
            store_chat_data=store_chat_data,
            store_bot_data=store_bot_data,
        )

    def get_user_data(self):
        data = self.fb_user_data.get()
        output = self.convert_user_docs(data)
        user_data = defaultdict(dict, output)
        self.user_data = user_data
        return user_data

    def get_chat_data(self):
        data = self.fb_chat_data.get()
        output = self.convert_keys(data)
        chat_data = defaultdict(dict, output)
        self.chat_data = chat_data
        return chat_data

    def get_bot_data(self):
        return defaultdict(dict, self.fb_bot_data or {})

    def get_conversations(self, name):
        doc = self.fb_conversations.document(name).get()
        res = dict()
        if doc.exists:
            res = {literal_eval(k): v for k, v in doc.to_dict().items()}
        return res

    def update_conversation(self, name, key, new_state):
        if new_state:
            self.fb_conversations.document(name).set({str(key): new_state})
        else:
            self.fb_conversations.document(name).update({str(key): firestore.DELETE_FIELD})

    def update_user_data(self, user_id: int, data: UD) -> None:
        if data and self.user_data.get(user_id) != data:
            self.fb_user_data.document(str(user_id)).set(data)
            self.user_data = data

    def update_chat_data(self, chat_id, data):
        if data and self.chat_data != data:
            self.fb_chat_data.document(str(chat_id)).set(data)
            self.chat_data = data

    def update_bot_data(self, data):
        if data:
            self.fb_bot_data = data

    @staticmethod
    def convert_keys(data: List[DocumentSnapshot]):
        output = {}
        for doc in data:
            for k, v in doc.to_dict().items():
                if k.isdigit():
                    output[int(k)] = v
                else:
                    output[k] = v
        return output

    @staticmethod
    def convert_user_docs(data: List[DocumentSnapshot]):
        output = {}
        for doc in data:
            output[int(doc.id)] = doc.to_dict()
        return output
