#Copyright 2015 Jonathan Schober Jr
#!/usr/bin/env python
#
# Audio 2 channel volume analyser using MCP2307
#
# Audio from wav file on SD card
#
import alsaaudio as aa
import ConfigParser
import audioop
from time import sleep
import struct
import wave
import sys
from ArduinoCarPi import ArduinoCarPi
from random import randint
import  RPi.GPIO as GPIO
import thread
Config = ConfigParser.ConfigParser()
Config.read('Settings.cfg')
ARDUINO = Config.get('Arduino','Arduino') == "True"
print(Config.get('Arduino','Arduino'))
RED = 9
GREEN = 10
BLUE = 11
leds = []
#colors = [[127,255,0],[127,255,212],[255,62,150],[255,175,250],[255,175,255],[255,0,255],[150,50,255],[115,100,255],[39,64,250],[200,225,255],[30,144,255],[0,191,255],[0,200,255],[151,255,255],[0,255,120],[124,252,0],[255,255,0],[255,185,15],[238,154,0],[255,100,80],[255,180,180],[255,100,100]]
currentColor = [0,0,0]
if ARDUINO is True:
	print(ARDUINO)
	arduino = ArduinoCarPi.Arduino(Config.get('Arduino','Arduino_port'))
	arduino.registerLEDs(RED,GREEN,BLUE)
else:
 GPIO.setmode(GPIO.BCM)
 GPIO.setup(GREEN,GPIO.OUT)
 GPIO.setup(RED, GPIO.OUT)
 GPIO.setup(BLUE, GPIO.OUT)
 r = GPIO.PWM(RED,60)
 g = GPIO.PWM(GREEN,60)
 b = GPIO.PWM(BLUE,60)
brightness = 1.0
previous = 60
current = 1
die = False;
def lightLED(amplitude):
	global previous
	global current
	global die
	#print amplitude
	if amplitude >1000 :
		#print '\033[93m' + "WARNING, amplitude: " + str(amplitude)
		amplitude = 1000
	if amplitude > previous+80:
		changeColor(amplitude)
#		print("Higher:", amplitude-previous)
#		if current == 1:
#			new = 0;
#		else:
#			new = 1
#		die = True
#		leds[current].start(0)
#		leds[new].start(float((amplitude/10) * brightness))
#		fadeThread = thread.start_new_thread(fadeLED,(leds[current],leds[new],previous))
#		current = new
		#print(type(brightness))
#		leds[current].start(float((amplitude/10) * brightness));
#	if amplitude >990:
#		print("Amplitude: ",amplitude);
#		leds[0].start(float((amplitude/10) * brightness));
#		leds[1].start(float((amplitude/10) * brightness))
	color = currentColor
	lightRGB((color[0]/255.0)*amplitude,(color[1]/255.0)*amplitude,(color[2]/255.0)*amplitude)
	previous = amplitude
	
def fadeLED(led,led2, currentLight):
	die = False
	l1 = currentLight
	l2 = 0
	while l1 >0 :
		if(die):
			break;
		led.start(l1)
		l1 = l1-5
		l2 = l2+5
		sleep(0.001)
		led2.start(l2)
stop = False;
output =""
def setup(chunk,no_channels,sample_rate):
	global output
	output = aa.PCM(aa.PCM_PLAYBACK, aa.PCM_NORMAL)
        output.setchannels(no_channels)
        output.setrate(sample_rate)
	output.setperiodsize(chunk)

def start(song):
	global stop
	global output
	stop = False
	# Set up audio
	wavfile = wave.open(str(song),'r')
	sample_rate = wavfile.getframerate()
	no_channels = wavfile.getnchannels()
	chunk = 250
	setup(chunk, no_channels,sample_rate)
	if wavfile.getsampwidth() == 1:
		output.setformat(aa.PCM_FORMAT_U8)
  # Otherwise we assume signed data, little endian
	elif wavfile.getsampwidth() == 2:
		output.setformat(aa.PCM_FORMAT_S16_LE)
	elif wavfile.getsampwidth() == 3:
		output.setformat(aa.PCM_FORMAT_S24_LE)
	elif wavfile.getsampwidth() == 4:
		output.setformat(aa.PCM_FORMAT_S32_LE)
	else:
		raise ValueError('Unsupported format')
	print "Processing....."

	data = wavfile.readframes(chunk)
	while data!='':
		if stop is True:
			print "dying"
			break;
		processData(data)
		data = wavfile.readframes(chunk)

def processData(data):
	global output
	output.write(data)
        # Split channel data and find maximum volume
	channel_l=audioop.tomono(data, 2, 1.0, 0.0)
	channel_r=audioop.tomono(data, 2, 0.0, 1.0)
 	max_vol_factor =32.5
	max_l = audioop.max(channel_l,2)/max_vol_factor
	max_r = audioop.max(channel_r,2)/max_vol_factor
#    print("L:",max_l);
#    print("R:",max_r);
	lightLED((max_l + max_r)/2)


def lightRGB(red,green,blue):
	if ARDUINO:
		red = red*0.25
		green = green*0.25
		blue = blue*0.25
		arduino.lightRGB(red * brightness,green * brightness,blue * brightness);
	else:
		red = red * 0.1;
		green = green * 0.1;
		blue = blue * 0.1;
		r.start(red * brightness)
		g.start(green * brightness)
		b.start(blue * brightness)
	
def changeColor(amplitude):
	global arduino
	global colors
	global currentColor
	arduino.registerLEDs(RED,GREEN,BLUE);
	#if currentColor == (len(colors)-1):
	#	currentColor = 0
#	else:
#		currentColor += 1
        #currentColor = randint(0,len(colors)-1)
	#color = colors[currentColor]
	color = [randint(0,255),randint(0,255),randint(0,255)]
	color[randint(0,2)] = 255
#	for pixel in color:
#		if pixel == 0:
#			pixel = randint(0,255);
	if color[0] > 128:
		while (color[1] + color[2]) < 128:
			color[1] = randint(0,255)
			color[2] = randint(0,255)

	currentColor = color
	print color
	lightRGB((color[0]/255.0)*amplitude,(color[1]/255.0)*amplitude,(color[2]/255.0)*amplitude)
def stopMusic():
	global stop
	stop = True

