import spotipy
#import spotipy.util as util
#import spotipy.oauth2
#from spotipy import SpotifyException

class SongData():
    # These are some global configuration parameters for using the Spotipy API
    USERNAME = 'Isaiah Robert Grace'
    USER_ID = '12149734788' # Isaiah Robert Grace
    CLIENT_ID = '9b6ff36aec5442088e9043520640f941'
    CLIENT_SECRET = 'e5baf7417df54c979cb2be7e67a337f2'
    REDIRECT_URI = 'http://localhost:8080'
    PORT_NUMBER = 8080
    SCOPE = 'user-read-currently-playing'
    CACHE = '.spotipyoauthcache'

    def __init__(self):
        self.sp = API_object()
        playing_track = None
        audio_features = None
            
    def token():
        # Refresh the token if needed.
        # This will not call the spotify API unless the token in cache is expired
        return util.prompt_for_user_token(username=USERNAME,
                                          scope=SCOPE,
                                          client_id=CLIENT_ID,
                                          client_secret=CLIENT_SECRET,
                                          redirect_uri=REDIRECT_URI)

    def API_object():
        # construct the Spotipy API object
        return spotipy.Spotify(auth=token())

    def set_playing_track():
        self.playing_track = sp.current_user_playing_track()
        
    def get_playing_track():
        # returns a god awful dict from the spotify API
        return self.audio_features

    def set_audio_features():
        song_id = playing_track['item']['uri']
        
        self.audio_features = sp.audio_features([song_id])[0]
        
        # Add some more info to the dict to help out the Pi
        self.audio_features['song_id']    = song_id
        self.audio_features['name']       = playing_track['item']['name']
        self.audio_features['artist']     = playing_track['item']['artists'][0]['name']
        self.audio_features['is_playing'] = playing_track['is_playing']
        
    def get_audio_features():
        return self.audio_features
