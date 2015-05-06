#Copyright 2015 Jonathan Schober Jr
# -*- coding: utf-8 -*-
import ssl
from flask import Flask,request, render_template
from time import sleep
import CarPi
import random
import datetime
import CarSpotify
import RPi.GPIO as GPIO
import json
ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
#ctx.load_cert_chain("ssl.crt","ssl.key")
ctx.load_cert_chain("mycert1.cer","mycert1.key")
app = Flask(__name__)
CarSpotify.init()
@app.route("/")
def hello():
	table = ""
	for color in CarPi.colors:
		r = format(color[0],'x')
		g = format(color[1],'x')
		b = format(color[2],'x')
		if len(r) == 1:
			r = "0"+r
		if len(g) == 1:
			g = "0"+g
                if len(b) == 1:
                        b = "0"+b
		color
		color = "#"+r+g+b
		table = table+'<tr><td><input type="submit" value="'+color+'"style="background-color:'+color+';" ></td></tr>';
	templateData = {
		'title' : 'RPi Is Working!',
		'table': table
	}
	return render_template('gpioweb.html', **templateData)
@app.route("/resume")
def resume():
	CarSpotify.session.player.play(play=True)
        return ""
@app.route("/pause")
def pause():
	CarSpotify.session.player.play(play=False)
	return ""
@app.route("/currentBrightness")
def getBrightness():
	return str(CarPi.brightness)

@app.route("/setBrightness")
def setBrightness():
	CarPi.brightness = float(request.args["brightness"])
	return "";
@app.route("/RGB")
def LightRGB():
	CarPi.lightRGB(float(request.args["red"]),float(request.args["green"]),float(request.args["blue"]));
	return "";
@app.route("/search")
def search():
	#relogin()
#	print request.args["query"];
	search = CarSpotify.session.search(request.args["query"])
	search.load()
	tracks = []
	for t in search.tracks:
		try:
			tracks.append({"Name":str(t.name),"artist":str(t.artists[0].name),"link":str(t.link)})
		except:
			app.logger.error('an error occurrend, wonder why');
	return json.dumps(tracks)	
@app.route("/playlists")
def findPlaylists():
	playlistcontainer = CarSpotify.session.playlist_container;
	playlists = []
	for play in playlistcontainer:
		try:
			playlists.append({"Name":str(play.name),"link":str(play.link)})
		except:
			app.logger.error('an error occurrend, wonder why');
	return json.dumps(playlists)
@app.route("/playlistTracks")
def tracksForPlaylist():
	#relogin()
	playlist = CarSpotify.session.get_playlist(request.args["link"])
	tracks = []
        for t in playlist.tracks:
                try:
              	   tracks.append({"Name":str(t.name),"artist":str(t.artists[0].name),"link":str(t.link)})
                except:
                   app.logger.error('an error occurrend, wonder why');
        return json.dumps(tracks)
        
@app.route("/randomTrack")
def randomRPITrack():
	playlistcontainer = CarSpotify.session.playlist_container;
	RPI = None;
	for playlist in playlistcontainer:
		if "RPi-Download" in playlist.name:
			RPI = playlist
			break;
	track = random.choice(RPI.tracks)
	CarSpotify.playTrack(track)
	return "Playing "+track.name + " By " + track.artists[0].name	
@app.route("/playTitle")
def playTitle():
	search = CarSpotify.session.search(request.args["query"])
        search.load()
	track = search.tracks[0];
	CarSpotify.playTrack(track)
        return "Playing "+track.name + " By " + track.artists[0].name
@app.route("/playTrack")
def playTrack():
	#sleep(10)
	app.logger.error(request.args);
	track = CarSpotify.session.get_track(request.args["track_uri"]).load()
	CarSpotify.playTrack(track)
	return "Playing "+track.name + " By " + track.artists[0].name
#def relogin():
#	if CarSpotify.session.connection.state != CarSpotify.spotify.ConnectionState.LOGGED_IN:
		#CarSpotify.session.relogin()
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=443, debug=True, ssl_context=ctx)
