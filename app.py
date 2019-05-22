# -*- encoding: utf-8 -*-
from datetime import datetime

from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity
from esipy.exceptions import APIException

from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import Response
from flask import request
from flask import session
from flask import url_for

from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

from classes.finance import Finance
# from classes.db import MongoDB
from classes.helpers import *
from classes.static import *
from classes.trade import *
from string import ascii_letters, digits
from random import SystemRandom

from classes import config
import hashlib
import hmac
import json
import logging
import time

# logger stuff
logger = logging.getLogger(__name__)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logger.addHandler(console)

# init app and load conf
flask = Flask(__name__)
flask.config.from_object(config)

# init db
db = SQLAlchemy(flask)
migrate = Migrate(flask, db)
# mongo = MongoDB()

# init flask login
login_manager = LoginManager()
login_manager.init_app(flask)
login_manager.login_view = 'login'


# -----------------------------------------------------------------------
# Database models
# -----------------------------------------------------------------------
class User(db.Model, UserMixin):
    # our ID is the character ID from EVE API
    character_id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=False
    )
    character_owner_hash = db.Column(db.String(255))
    character_name = db.Column(db.String(200))

    # SSO Token stuff
    access_token = db.Column(db.String(4096))
    access_token_expires = db.Column(db.DateTime())
    refresh_token = db.Column(db.String(100))

    def get_id(self):
        """ Required for flask-login """
        return self.character_id

    def get_sso_data(self):
        """ Little "helper" function to get formated data for esipy security
        """
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_in': (
                    self.access_token_expires - datetime.utcnow()
            ).total_seconds()
        }

    def update_token(self, token_response):
        """ helper function to update token data from SSO response """
        self.access_token = token_response['access_token']
        self.access_token_expires = datetime.fromtimestamp(
            time.time() + token_response['expires_in'],
        )
        if 'refresh_token' in token_response:
            self.refresh_token = token_response['refresh_token']


# -----------------------------------------------------------------------
# Flask Login requirements
# -----------------------------------------------------------------------
@login_manager.user_loader
def load_user(character_id):
    """ Required user loader for Flask-Login """
    return User.query.get(character_id)


# -----------------------------------------------------------------------
# ESIPY Init
# -----------------------------------------------------------------------
# create the app
app = EsiApp().get_latest_swagger

# init the security object
security = EsiSecurity(
    redirect_uri=config.ESI_CALLBACK,
    client_id=config.ESI_CLIENT_ID,
    secret_key=config.ESI_SECRET_KEY,
    headers={'User-Agent': config.ESI_USER_AGENT},
    retry_requests=True,
    raw_body_only=False
)

# init the client
client = EsiClient(
    security=security,
    cache=None,
    headers={'User-Agent': config.ESI_USER_AGENT}
)


# -----------------------------------------------------------------------
# Login / Logout Routes
# -----------------------------------------------------------------------
def generate_token():
    """Generates a non-guessable OAuth token"""
    chars = (ascii_letters + digits)
    rand = SystemRandom()
    random_string = ''.join(rand.choice(chars) for _ in range(len(chars)))
    return hmac.new(
        config.SECRET_KEY.encode('utf-8'),
        random_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


@flask.route('/sso/login')
def login():
    """ this redirects the user to the EVE SSO login """
    token = generate_token()
    session['token'] = token
    return redirect(security.get_auth_uri(
        state=token,
        scopes=config.ESI_SCOPES
    ))


@flask.route('/sso/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@flask.route('/sso/callback')
def callback():
    """ This is where the user comes after he logged in SSO """
    # get the code from the login process
    code = request.args.get('code')
    token = request.args.get('state')

    # compare the state with the saved token for CSRF check
    sess_token = session.pop('token', None)
    if sess_token is None or token is None or token != sess_token:
        return 'Login EVE Online SSO failed: Session Token Mismatch', 403

    # now we try to get tokens
    try:
        auth_response = security.auth(code)
    except APIException as e:
        return 'Login EVE Online SSO failed: %s' % e, 403

    # we get the character informations
    cdata = security.verify()

    # if the user is already authed, we log him out
    if current_user.is_authenticated:
        logout_user()

    # now we check in database, if the user exists
    # actually we'd have to also check with character_owner_hash, to be
    # sure the owner is still the same, but that's an example only...
    try:
        user = User.query.filter(
            User.character_id == cdata['sub'].split(':')[2],
        ).one()

    except NoResultFound:
        user = User()
        user.character_id = cdata['sub'].split(':')[2]

    user.character_owner_hash = cdata['owner']
    user.character_name = cdata['name']
    user.update_token(auth_response)

    # now the user is ready, so update/create it and log the user
    try:
        db.session.merge(user)
        db.session.commit()

        login_user(user)
        session.permanent = True
    except:
        logger.exception("Cannot login the user - uid: %d" % user.character_id)
        db.session.rollback()
        logout_user()

    return redirect(url_for("index"))


# -----------------------------------------------------------------------
# Index Routes
# -----------------------------------------------------------------------
# Check auth
@flask.route('/')
@login_required
def index():
    if current_user.is_authenticated:
        security.update_token(current_user.get_sso_data())

    m = Markets(app, client)
    m.get_space_rich()

    return Response('done!')  # mimetype='application/json')


@flask.route('/debug')
@login_required
def debug():
    if current_user.is_authenticated:
        # Give the token data to esisecurity
        # it will check if the access token need some update
        security.update_token(current_user.get_sso_data())
    # else:
    #     return redirect(url_for('/sso/login'))

    f = Finance(id_char=current_user.character_id, app=app, client=client)

    data = {'date': time.time(), 'total': f.get_data('wallet')}

    # f.write_mongo_data('wallet', [data], update=False)

    return render_template('base.html', **{
        'data': data['total'],
    })

###################################################################################################
###################################################################################################
###################################################################################################
# DEBUG
@flask.route('/test')
@login_required
def test():
    if current_user.is_authenticated:
        security.update_token(current_user.get_sso_data())

    f = Finance(current_user.character_id, app, client)

    data = {
        'date': time.time(),
        'wallet_total': f.get_data('wallet'),
        'wallet_journal': f.get_data('wallet_journal'),
        'wallet_transactions': f.get_data('wallet_transactions')
    }

    # f.write_mongo_data('wallet', [data], update=False)

    return render_template('base.html', **{
        'data': data,
    })



###################################################################################################
###################################################################################################
###################################################################################################
@flask.route('/wJournal')
@login_required
def wJournal():
    if current_user.is_authenticated:
        # Give the token data to esisecurity
        # it will check if the access token need some update
        security.update_token(current_user.get_sso_data())

    f = Finance(app=app, client=client, id_char=current_user.character_id)

    data = f.get_data('wallet_journal')[0]
    # f.write_mongo_data('wallet_journal', data, update=False)

    # return jsonify({'data': data})
    return Response(json.dumps(data), mimetype='application/json')


@flask.route('/wTransactions')
@login_required
def wTransactions():
    if current_user.is_authenticated:
        # Give the token data to esisecurity
        # it will check if the access token need some update
        security.update_token(current_user.get_sso_data())

    f = Finance(app, client, id_char=current_user.character_id)

    data = f.get_data('wallet_transactions')[0]
    # f.write_mongo_data('wallet_transactions', data[0], update=False)

    # return jsonify(data)
    return Response(json.dumps(data), mimetype='application/json')


if __name__ == '__main__':
    flask.run(port=config.PORT, host=config.HOST)
