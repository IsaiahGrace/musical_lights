import spotipy
from termcolor import colored

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
        self.messages = []

        
    def token(self):
        # Refresh the token if needed.
        # This will not call the spotify API unless the token in cache is expired
        return spotipy.util.prompt_for_user_token(username=self.USERNAME,
                                          scope=self.SCOPE,
                                          client_id=self.CLIENT_ID,
                                          client_secret=self.CLIENT_SECRET,
                                          redirect_uri=self.REDIRECT_URI)

    def init_sp(self):
        # construct the Spotipy API object
        self.sp = spotipy.Spotify(auth=self.token())
        #print(colored('Refreshed token from Spotify','yellow'))
        self.messages.append('Refreshed token from Spotify')
        
    def set_playing_track(self):
        self.playing_track = self.sp.current_user_playing_track()
        
    def get_playing_track(self):
        # returns a god awful dict from the spotify API
        return self.audio_features

    def set_audio_features(self):
        song_id = self.playing_track['item']['uri']
        self.audio_features = self.sp.audio_features([song_id])[0]
            
        # Add some more info to the dict to help out the Pi
        self.audio_features['song_id']    = song_id
        self.audio_features['name']       = self.playing_track['item']['name']
        self.audio_features['artist']     = self.playing_track['item']['artists'][0]['name']
        self.audio_features['is_playing'] = self.playing_track['is_playing']
        
        #print(colored('Got info about "' + self.audio_features['name'] + '" from Spotify','yellow'))
        self.messages.append('Got info about "' + self.audio_features['name'] + '" from Spotify')


    def collect_messages(self):
        return self.messages
        
    def get_audio_features(self):
        return self.audio_features

    def song_id(self):
        return self.audio_features['song_id']
