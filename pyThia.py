import pickle
import redis
import webbrowser
from esipy import EsiApp
from esipy import EsiClient
from esipy import EsiSecurity
from esipy.cache import RedisCache
# from esipy.utils import generate_code_verifier
from classes import config, helpers, trade


esi_app = EsiApp()
app = esi_app.get_latest_swagger

redis_client = redis.Redis(host='localhost', port=6379, db=0)
cache = RedisCache(redis_client)

# init the security object
security = EsiSecurity(
    redirect_uri=config.ESI_CALLBACK,
    client_id=config.ESI_CLIENT_ID,
    secret_key=config.ESI_SECRET_KEY,
    # code_verifier=generate_code_verifier()
    headers={'User-Agent': config.ESI_USER_AGENT}
)

# init the client
client = EsiClient(
    cache=cache,
    security=security,
    headers={'User-Agent': config.ESI_USER_AGENT},
    retry_requests=True,
)



### Authenticate
eve_sso_auth_url = security.get_auth_uri(
    state=helpers.generate_state_token(),
    # scopes=config.ESI_SCOPES  # or None (default) if you don't need any scope
    scopes=['publicData']
)

webbrowser.open_new_tab(eve_sso_auth_url)

code = input('Code: ')

tokens = security.auth(code)
security.verify()

m = trade.Markets(app, client)
# m.get_space_rich_jita()
m.get_space_rich_amarr()

print('debug')
