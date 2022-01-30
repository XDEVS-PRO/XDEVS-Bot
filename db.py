from google.cloud.firestore_v1 import DocumentReference, DocumentSnapshot

from settings import firestore_client as client


def get_or_create(collection: str, doc: str, data: dict) -> DocumentReference:
    doc_ref = client.collection(collection).document(doc)
    doc = doc_ref.get()
    if doc.exists:
        return doc
    else:
        doc_ref.set(data)
    return doc_ref


def get_user(username: str) -> DocumentSnapshot:
    return client.collection('users').document(username).get()


def update_user(username: str, data: dict):
    client.collection('users').document(username).set(data, merge=True)


def patch_user(username: str, data: dict):
    client.collection('users').document(username).update(data)
