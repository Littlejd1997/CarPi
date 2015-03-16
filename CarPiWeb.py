#Copyright 2015 Jonathan Schober Jr
# -*- coding: utf-8 -*-
from flask import Flask,request, render_template
import CarPi
import datetime
import CarSpotify
import RPi.GPIO as GPIO
import json
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
	playlist = CarSpotify.session.get_playlist(request.args["link"])
	tracks = []
        for t in playlist.tracks:
                try:
                        tracks.append({"Name":str(t.name),"artist":str(t.artists[0].name),"link":str(t.link)})
                except:
                        app.logger.error('an error occurrend, wonder why');
        return json.dumps(tracks)
@app.route("/playTrack")
def playTrack():
	app.logger.error(request.args);
	track = CarSpotify.session.get_track(request.args["track_uri"]).load()
	CarSpotify.playTrack(track)
	return "Playing "+track.name + " By " + track.artists[0].name
if __name__ == "__main__":
   app.run(host='0.0.0.0', port=85, debug=True)
