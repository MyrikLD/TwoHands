import fcntl
import json
import random
import socket
import struct
import urllib
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from cv2 import imshow, namedWindow, setWindowProperty
from platform import machine
from threading import Thread
import re

import cv2
import numpy as np

from btns import desk, Button

STAGE = 0
LANCAM = list()
WindowName = 'Term'
FULLSCREEN = True

with open('settings.json') as json_data:
	settings = json.load(json_data)


class CamHandler(BaseHTTPRequestHandler):
	streams = None

	def do_GET(self):
		name = self.path[1:self.path.find('.')]

		if self.path.endswith('.btn'):
			self.send_response(200)
			game.netClick(desk.get(name))

		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
			self.end_headers()
			while True:
				try:
					num = int(name)
					img = self.streams[num].img()
					if img is not None:
						img = img.tostring()
					else:
						continue

					self.wfile.write('--jpgboundary\r\n')
					self.send_header('Content-type', 'image/jpeg')
					self.send_header('Content-length', str(len(img)))
					self.end_headers()
					self.wfile.write(img)
				except KeyboardInterrupt:
					break
			return
		if self.path.endswith('.html'):
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write('<html><head></head><body>')
			self.wfile.write('<img src="/%s.mjpg"/>' % int(name))
			self.wfile.write('</body></html>')


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""


class VideoStream:
	frame = None
	grabbed = None
	stream = None
	stopped = True
	src = None

	ip = ''
	port = ''
	fn = ''
	ft = ''
	net = None

	def __init__(self, src=0):
		if type(src) == int:
			self.src = src
			self.stream = cv2.VideoCapture(src)
			(self.grabbed, self.frame) = self.stream.read()
		else:
			pattern = r"^http:\/\/(?P<ip>[0-9.]+):(?P<port>[0-9]+)\/(?P<fn>.+)\.(?P<ft>.+)$"
			self.net = re.search(pattern, src).groupdict()

			self.src = str(src)

	def start(self):
		self.stopped = False
		Thread(target=self.update, args=()).start()
		return self

	def update(self):
		if type(self.src) == str:
			stream = None
			while stream is None:
				try:
					stream = urllib.urlopen(self.src)
				except Exception as e:
					print(self.src + ': ' + str(e))
			data = bytes()
			while True:
				if self.stopped:
					return

				data += stream.read(1)
				a = data.find(b'--')
				b = data.find(b'\r\n\r\n')

				if a != -1 and b != -1:
					head = data[a:b].split('\r\n')
					for i in head:
						if 'length' in i:
							l = int(i[i.find(': ') + 2:])

					jpg = bytes()
					data = bytes()
					while len(jpg) < l:
						jpg += stream.read(l - len(jpg))

					self.frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

		else:
			while True:
				if self.stopped:
					return
				(self.grabbed, self.frame) = self.stream.read()

	def read(self):
		return self.frame

	def img(self):
		if self.frame is not None:
			return cv2.imencode(".png", self.read())[1]
		else:
			return None

	def stop(self):
		self.stopped = True

	def __del__(self):
		self.stop()
		self.stream.release()


def getImg(c):
	for i in c:
		yield i.read()


def comp(*img):
	img = list(img)

	for i in range(len(img)):
		if None in img:
			img.remove(None)

	if len(img) == 0:
		vis = np.zeros((1, 1), np.uint8)
		frame = cv2.resize(vis, tuple(settings['size']))
		return frame

	h = [i.shape[0] for i in img]
	w = [i.shape[1] for i in img]

	sz = (max(h), sum(w), 3)

	# Create an array big enough to hold both images next to each other.
	vis = np.zeros(sz, np.uint8)
	# Copy both images into the composite image.
	for i in range(len(img)):
		vis[:h[i], sum(w[:i]):sum(w[:(i + 1)])] = img[i]

	frame = cv2.resize(vis, tuple(settings['size']))
	return frame


cam = list([VideoStream(0).start(), VideoStream(1).start()])


# VideoStream('http://127.0.0.1:81/0.mjpg')

class Game:
	stage = 0
	round = 0
	btns = list()

	def __init__(self):
		Button.callback = self.clicked
		self.getRandBtns()

	def getRandBtns(self):
		desk.leds(False)
		for i in desk.L:
			i.clicked = False
		for i in desk.R:
			i.clicked = False

		self.btns = list([random.choice(desk.L), random.choice(desk.R)])
		for i in self.btns:
			i.led(True)

	def netClick(self, btn):
		if btn not in self.btns:
			self.round = 0
			self.getRandBtns()
		else:
			btn.led(False)
			self.btns.remove(btn)
			if len(self.btns) == 0:
				self.nextRound()

	def _nextStage(self):
		self.stage += 1
		print('next stage: ' + str(self.stage))
		self.round = 0
		self.getRandBtns()

	def nextRound(self):
		self.round += 1

		if self.round > 3:
			self._nextStage()
		else:
			print('next round: ' + str(self.round))
			self.getRandBtns()

	def resetRound(self):
		print('reset round')
		self.round = 0
		self.getRandBtns()

	def clicked(self, btn):
		print(btn.pos + str(btn.num))
		if self.stage <= 2:
			if btn not in self.btns:
				self.resetRound()
			else:
				btn.led(False)
				if self.btns[0].clicked and self.btns[1].clicked:
					self.nextRound()
		else:

			if self.stage == 4:
				a = list([LANCAM[-(i + 1)] for i in range(len(LANCAM))])
			else:
				a = list(LANCAM)

			if btn.pos == 'left':
				net = a[0].net
			else:
				net = a[1].net
			url = 'http://' + str(net['ip']) + ':' + str(net['port']) + '/' + str(btn) + '.btn'
			url = urllib.urlopen(url)
			a = url.getcode()
			print(str(url)+' '+str(a))
			url.close()


game = Game()


def createFrame():
	frames = list()
	if game.stage == 0:
		frames = getImg(cam)
	elif game.stage == 1:
		a = list([cam[-(i + 1)] for i in range(len(cam))])
		frames = getImg(a)
	elif game.stage == 2:
		for i in LANCAM:
			if i.stopped:
				i.start()
		frames = getImg(LANCAM)
	elif game.stage == 3:
		for i in LANCAM:
			if i.stopped:
				i.start()
		a = list([LANCAM[-(i + 1)] for i in range(len(LANCAM))])
		frames = getImg(a)

	frame = comp(*frames)
	return frame


def window(*cam):
	global STAGE

	while (True):
		frame = createFrame()

		if frame is not None:
			imshow(WindowName, frame)

		key = cv2.waitKey(1)

		if key & 0xFF == 27:
			break

		if key & 0xFF == 32:
			STAGE = (STAGE + 1) % 3

	cam[0].stop()
	cam[1].stop()
	cv2.destroyAllWindows()
	exit(-1)


def serve():
	CamHandler.streams = cam
	server = ThreadedHTTPServer(('', settings['port']), CamHandler)
	print("server started")
	server.serve_forever()


def get_ip_address(ifname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	try:
		addr = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])
	except:
		addr = None
	return addr


if __name__ == '__main__':
	ip = get_ip_address('wlan0' if machine() == 'armv7l' else 'wlp3s0')
	WindowName = str(ip)
	other = settings.get(ip, [])

	if FULLSCREEN:
		namedWindow(WindowName, cv2.WND_PROP_FULLSCREEN)
		setWindowProperty(WindowName, cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

	th = Thread(target=window, args=(cam)).start()
	th1 = Thread(target=serve, args=()).start()
	Thread(target=window, args=(cam))

	LANCAM = list()
	for i in other:
		d = VideoStream('http://%s:81/%s.mjpg' % (i[0], i[1]))
		LANCAM.append(d)
	print(other)
