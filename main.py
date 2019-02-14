# -*- encoding: utf-8 -*-
from datetime import datetime
import configparser
import random
import hashlib
import hmac

from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity
from esipy.exceptions import APIException

from flask import Flask


config = configparser.ConfigParser()
config.read('pyThia.cfg')

# -----------------------------------------------------------------------
# ESIPY Init
# -----------------------------------------------------------------------
# create the app
esiApp = EsiApp()
# esiCurrent = esiApp.get_latest_swagger()

# init the security object
esiSecurity = EsiSecurity(
    redirect_uri=config['ESI']['CALLBACK'],
    client_id=config['ESI']['CLIENT_ID'],
    secret_key=config['ESI']['SECRET_KEY'],
    headers={'User-Agent': config['ESI']['USER_AGENT']}
)

# init the client
esiClient = EsiClient(
    security=esiSecurity,
    cache=None,
    headers={'User-Agent': config['ESI']['USER_AGENT']}
)


# -----------------------------------------------------------------------
# Login / Logout Routes
# -----------------------------------------------------------------------
def generate_token():
    """Generates a non-guessable OAuth token"""
    chars = ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    rand = random.SystemRandom()
    random_string = ''.join(rand.choice(chars) for _ in range(40))
    return hmac.new(
        config['ESI']['SECRET_KEY'].encode('utf-8'),
        random_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

token = generate_token()
esiSecurity.get_auth_uri(state=token, scopes=['esi-wallet.read_character_wallet.v1'])