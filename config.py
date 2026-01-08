import os

class Config:
    API_ID = int(os.getenv('API_ID', 0))
    API_HASH = os.getenv('API_HASH', '')
    SESSION_STRING = os.getenv('SESSION_STRING', '')
