import os

import firebase_admin
from firebase_admin import credentials, firestore
from storage.firebase_persistance import FirebasePersistence

DEBUG = (os.getenv('DEBUG', 'False') == 'True')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')
cred = credentials.Certificate("./firebase.json")

firebase_admin.initialize_app(cred)
firestore_client = firestore.client()

firebase_persistence = FirebasePersistence(client=firestore_client)
