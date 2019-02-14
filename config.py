# -*- encoding: utf-8 -*-
import datetime

# -----------------------------------------------------
# Application configurations
# ------------------------------------------------------
DEBUG = True
SECRET_KEY = 'W422dbfb58MrGTN6EaDPfAkDM1s'
PORT = 42001
HOST = 'localhost'

# -----------------------------------------------------
# SQL Alchemy configs
# -----------------------------------------------------
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'

# -----------------------------------------------------
# ESI Configs
# -----------------------------------------------------
ESI_DATASOURCE = 'tranquility'  # Change it to 'singularity' to use the test server
ESI_SWAGGER_JSON = 'https://esi.evetech.net/latest/swagger.json?datasource=%s' % ESI_DATASOURCE
ESI_SECRET_KEY = 'Kt64vJzwfK6dDd81B2EJ4u8YsKHJAcbNwUXl0GXA'  # your secret key
ESI_CLIENT_ID = '58f938219867468099c3569cffedf366'  # your client ID
ESI_CALLBACK = 'http://%s:%d/sso/callback' % (HOST, PORT)  # the callback URI you gave CCP
ESI_USER_AGENT = 'pyThia'


# ------------------------------------------------------
# Session settings for flask login
# ------------------------------------------------------
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)

# ------------------------------------------------------
# DO NOT EDIT
# Fix warnings from flask-sqlalchemy / others
# ------------------------------------------------------
SQLALCHEMY_TRACK_MODIFICATIONS = True