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


config = configparser.ConfigParser()
config.read('pyThia.cfg')

# -----------------------------------------------------------------------
# ESIPY Init
# -----------------------------------------------------------------------
# create the app
esiapp = EsiApp().get_latest_swagger

# init the security object
esisecurity = EsiSecurity(
    redirect_uri=config['global']['ESI_CALLBACK'],
    client_id=config['global']['ESI_CLIENT_ID'],
    secret_key=config['global']['ESI_SECRET_KEY'],
    headers={'User-Agent': config['global']['ESI_USER_AGENT']}
)

# init the client
esiclient = EsiClient(
    security=esisecurity,
    cache=None,
    headers={'User-Agent': config['global']['ESI_USER_AGENT']}
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
        config['global']['SECRET_KEY'].encode('utf-8'),
        random_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

token = generate_token()
esisecurity.get_auth_uri(state=token, scopes=['esi-wallet.read_character_wallet.v1'])