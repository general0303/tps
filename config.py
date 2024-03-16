import os


class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:pass@127.0.0.1:3306/tps'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
