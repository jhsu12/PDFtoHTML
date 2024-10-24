import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL")
    MODEL_NAME = os.getenv("MODEL_NAME")
    TEMPERATURE = os.getenv("TEMPERATURE")
    ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "[*]")
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    DEBUG = True
    TESTING = True

def get_config():
    env = os.getenv('ENV', 'dev')
    if env == 'prod':
        return Config()
    elif env == 'test':
        return TestingConfig()
    else:
        return DevelopmentConfig()
