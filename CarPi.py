
#!/usr/bin/env python
#
# Audio 2 channel volume analyser using MCP2307
#
# Audio from wav file on SD card
#
import alsaaudio as aa
import audioop
from time import sleep
import struct
import wave
import sys
from random import randint
import  RPi.GPIO as GPIO
import thread

GREEN = 21
RED = 20
BLUE = 4
leds = []
colors = [[255,62,150],[139,71,137],[139,102,139],[139,0,139],[138,43,226],[105,89,205],[39,64,250],[112,128,144],[30,144,255],[0,191,255],[0,197,205],[151,255,255],[0,205,102],[124,252,0],[255,255,0],[255,185,15],[238,154,0],[139,69,19],[188,143,143],[128,50,50]]
currentColor = 0
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
		changeColor()
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
	r.start(red * brightness)
	g.start(green * brightness)
	b.start(blue * brightness)
def changeColor():
	global colors
	global currentColor
	#if currentColor == (len(colors)-1):
	#	currentColor = 0
#	else:
#		currentColor += 1
        currentColor = randint(0,len(colors)-1)
	color = colors[currentColor]
	lightRGB((color[0]/255.0)*100,(color[1]/255.0)*100,(color[2]/255.0)*100)
def stopMusic():
	global stop
	stop = True

