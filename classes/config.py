# -*- encoding: utf-8 -*-
import datetime

# -----------------------------------------------------
# Application configurations
# ------------------------------------------------------
DEBUG = True
SECRET_KEY = 'ChangeMe!'
PORT = 42001
HOST = 'localhost'

# -----------------------------------------------------
# Mongo Database configurations
# ------------------------------------------------------
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGODB_USER = 'root'
MONGODB_PASS = 'ChangeMe!'


# -----------------------------------------------------
# SQL Alchemy configs
# -----------------------------------------------------
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'

# -----------------------------------------------------
# ESI Configs
# -----------------------------------------------------
ESI_CLIENT_ID = 'ChangeMe!'  # your client ID
ESI_CALLBACK = 'http://%s:%d/sso/callback' % (HOST, PORT)  # the callback URI you gave CCP
ESI_DATASOURCE = 'tranquility'  # Change it to 'singularity' to use the test server
ESI_SWAGGER_JSON = 'https://esi.evetech.net/latest/swagger.json?datasource=%s' % ESI_DATASOURCE
ESI_SECRET_KEY = 'ChangeMe!'  # your secret key
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
