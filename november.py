import RPi.GPIO as GPIO
from time import sleep
from picamera import PiCamera
from io import BytesIO
import boto3
import subprocess

GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

left = GPIO.PWM(11, 50)
right = GPIO.PWM(12, 50)
left.start(0)
right.start(0)
left.ChangeDutyCycle(13)
right.ChangeDutyCycle(4)

camera = PiCamera()
camera.rotation = 90

rekognition = boto3.client('rekognition', region_name='us-west-2')

SCARY_THINGS = [
	'Rat',
	'Mouse',
	'Mole',
	'Rodent',
	'Pumpkin',
	'Skeleton',
	'Spider'
]

def coverEyes():
	left.ChangeDutyCycle(4)
	right.ChangeDutyCycle(13)

def revealEyes():
	left.ChangeDutyCycle(13)
	right.ChangeDutyCycle(4)

if __name__ == '__main__':
	fearFactor = 0
	while True:
		with BytesIO() as imageStream:
			camera.capture(imageStream, 'jpeg')
			response = rekognition.detect_labels(Image={'Bytes': bytes(imageStream.getbuffer())}, MaxLabels=100, MinConfidence=30.0)
			scared = False
			for label in response['Labels']:
				print(label['Name'])
				if label['Name'] in SCARY_THINGS:
					print('EEK! A', label['Name'])
					if fearFactor != 3:
						subprocess.Popen(['/usr/bin/aplay', 'alert.wav'])
					coverEyes()
					scared = True
					fearFactor = 3
					break
			if not scared:
				print('Nothing scary! Nice!')
				fearFactor -= 1
				if fearFactor <= 0:
					revealEyes()
		print('Fear factor', str(fearFactor))
		sleep(1)