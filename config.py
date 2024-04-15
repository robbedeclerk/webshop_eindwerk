import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI') or (f"postgresql://"
                                                           f"{os.environ.get('DB_USER')}:"
                                                           f"{os.environ.get('DB_USER_PASSWORD')}"
                                                           f"@{os.environ.get('DB_HOST')}"
                                                           f"/{os.environ.get('DB_NAME')}"
                                                           )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #MAIL_SERVER = os.environ.get('MAIL_SERVER')
    #MAIL_PORT =587
    #MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    #MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = os.environ.get('ADMINS')