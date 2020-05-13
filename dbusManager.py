import dbus

# This class uses the dbus to interact with the open spotipy desktop client
class DbusManager:
    def __init__(self):
        self.player = None

    # Returns true if spotify can be reached
    def connect_to_spotify(self):
        try:
            self.player = MediaPlayer("spotify")
        except dbus.exceptions.DBusException:
            self.player = None
        return True if self.player else False

    # This method is not used right now, but it might be useful someday
    def get_song_name(self):
        if not self.player:
            return None
        return self.player.song_name()

    # This method is not used right now, but it might be useful someday
    def get_song_info(self):
        if not self.player:
            return None
        return self.player.song_string()

    def isOpen(self):
        return True if self.player else False
        
    def isPlaying(self):
        if not self.player:
            return False
        try:
            playing = self.player.isPlaying()
        except dbus.exceptions.DBusException:
            self.player = None
            playing = False
            
        return playing
            


class MediaPlayer:
    # gist.github.com/FergusInLondon
    # https://gist.github.com/FergusInLondon/960ebd9c50d5abe1eafbead9ead7dc42
    # MediaPlayer class from FergusInLondon, with modifications
    # Recieves state from a MediaPlayer using dbus.
    player_properties = False

    def __init__(self, player_name):
        # Get an instance of the dbus session bus, and retrieve
        #  a proxy object for accessing the MediaPlayer
        session_bus = dbus.SessionBus()
        player_proxy = session_bus.get_object(
            'org.mpris.MediaPlayer2.%s' % player_name,
            '/org/mpris/MediaPlayer2')
        
        
        # Apply the interface 'org.freedesktop.DBus.Properties to
        #  the player proxy, allowing us to call .Get() and .GetAll()
        self.player_properties = dbus.Interface(player_proxy, 'org.freedesktop.DBus.Properties')
    
    # Retrieve the properties from the Player interface, return a song string.
    def song_string(self):
        props = self.player_properties.GetAll('org.mpris.MediaPlayer2.Player')
        return "%s, %s, %s" % (props["Metadata"]["xesam:artist"][0],
                               props["Metadata"]["xesam:title"],
                               props["Metadata"]["xesam:album"])
    
    def song_name(self):
        # Written by Isaiah
        props = self.player_properties.GetAll('org.mpris.MediaPlayer2.Player')
        return "%s" % (props["Metadata"]["xesam:title"])
            
    def isPlaying(self):
        # Written by Isaiah
        props = self.player_properties.GetAll('org.mpris.MediaPlayer2.Player')
        if props['PlaybackStatus'] == 'Playing':
            return True
        else:
            return False
