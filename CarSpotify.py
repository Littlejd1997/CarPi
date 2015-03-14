#Copyright 2015 Jonathan Schober Jr
#!/usr/bin/env python
from __future__ import unicode_literals
import sys
import threading
import spotify
from time import sleep
import lightnew
import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read('Settings.cfg')
def on_connection_state_updated(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()


def on_end_of_track(self):
    global session
    end_of_track.set()

def deliverMusic(session, format,data,num_frames):
	global setup
	if setup is False:
		print format
		lightnew.setup(num_frames,format.channels,format.sample_rate)
		setup = True
	lightnew.processData(data)
	return num_frames

session = None
setup = False
hasInitted = False
def init():
	global hasInitted
	if hasInitted is False:
		realInit();
		hasInitted = True
def realInit():
	global session
# Assuming a spotify_appkey.key in the current dir
	config = spotify.Config();
	config.load_application_key_file(filename=Config.get('Spotify','apikey'))
	session = spotify.Session(config)
	loop = spotify.EventLoop(session)
	loop.start()
	session.on(spotify.SessionEvent.MUSIC_DELIVERY, deliverMusic)

	session.login(Config.get('Spotify','username'),Config.get('Spotify','password'))
	session.preferred_bitrate(spotify.Bitrate.BITRATE_96k)

def playTrack(track):
	global session
# Play a track
	session.player.load(track)
	session.player.play()
