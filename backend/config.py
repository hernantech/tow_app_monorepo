import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    WECHAT_APP_ID = os.getenv('WECHAT_APP_ID', '')
    WECHAT_APP_SECRET = os.getenv('WECHAT_APP_SECRET', '')
    WECHAT_TOKEN = os.getenv('WECHAT_TOKEN', 'default_token')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///intake.db')

class TestConfig(Config):
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
    JWT_SECRET_KEY = 'test-secret-key'
    WECHAT_TOKEN = 'test_token'
