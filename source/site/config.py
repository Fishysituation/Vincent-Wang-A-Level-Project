"""
site configurations
"""

class Config(object):
    SECRET_KEY = 'secret-key'
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
