import spotipy
import spotipy.util as util
import spotipy.oauth2
from spotipy import SpotifyException

# These are some global configuration parameters for using the Spotipy API
USERNAME = 'Isaiah Robert Grace'
USER_ID = '12149734788' # Isaiah Robert Grace
CLIENT_ID = '9b6ff36aec5442088e9043520640f941'
CLIENT_SECRET = 'e5baf7417df54c979cb2be7e67a337f2'
REDIRECT_URI = 'http://localhost:8080'
PORT_NUMBER = 8080
SCOPE = 'user-read-currently-playing'
CACHE = '.spotipyoauthcache'
