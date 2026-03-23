import os
from dotenv import load_dotenv, set_key
from pathlib import Path

env_path = Path(__file__).parent / 'config.env'
load_dotenv(dotenv_path=env_path)

class Config:
    def __init__(self):
        self.STORAGE_DATA_AUTH = os.getenv('STORAGE_DATA_AUTH')
        self.STORAGE_DATA_AUTH_CALLS = os.getenv('STORAGE_DATA_AUTH_CALLS')
        self.TG_TOKEN = os.getenv('TG_TOKEN')
        self.URL = os.getenv('URL')
        self.CURRENT_DATAINDEX = os.getenv('CURRENT_DATAINDEX')
        self.GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')
        self.DELAY_REQUESTING = os.getenv('DELAY_REQUESTING')
        self.STATUS_REQUSTING = os.getenv('STATUS_REQUSTING')
        self.TRACKER_DEVICE_ID = os.getenv('TRACKER_DEVICE_ID')


    
    def refresh(self):
        load_dotenv(dotenv_path=env_path, override=True)
        self.STORAGE_DATA_AUTH = os.getenv('STORAGE_DATA_AUTH')
        self.STORAGE_DATA_AUTH_CALLS = os.getenv('STORAGE_DATA_AUTH_CALLS')
        self.TG_TOKEN = os.getenv('TG_TOKEN')
        self.URL = os.getenv('URL')
        self.CURRENT_DATAINDEX = os.getenv('CURRENT_DATAINDEX')
        self.GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')
        self.DELAY_REQUESTING = os.getenv('DELAY_REQUESTING')
        self.STATUS_REQUSTING = os.getenv('STATUS_REQUSTING')
        self.TRACKER_DEVICE_ID = os.getenv('TRACKER_DEVICE_ID')
        
config = Config()

def update_env(key, new_value):
    set_key(env_path, key, new_value)
    config.refresh()
    
    print(f"| Successful edited, now: {key} = {getattr(config, key)}")
