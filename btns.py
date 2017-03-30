try:
	import RPi.GPIO as GPIO

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
except RuntimeError:
	class gpio:
		PUD_DOWN = 1
		PUD_UP = 2
		OUT = 3
		IN = 4
		FALLING = 5
		BOTH = 6

		def setup(self, *args, **kwargs):
			pass

		def add_event_detect(self, *args, **kwargs):
			pass

		def input(self, a):
			pass

		def output(self, *args, **kwargs):
			pass

		def remove_event_detect(self, *args, **kwargs):
			pass


	GPIO = gpio()

	print('Its not PI')

from time import sleep, time


class Button:
	ledPin = 0
	btnPin = 0

	ledState = False
	lp = 0
	clicked = False

	def __init__(self, b, l, pup=False):
		self.ledPin = l
		self.btnPin = b
		pup = (GPIO.PUD_UP if pup else GPIO.PUD_DOWN)

		GPIO.setup(l, GPIO.OUT)
		GPIO.setup(b, GPIO.IN, pull_up_down=pup)
		GPIO.add_event_detect(b, GPIO.BOTH, callback=self._callback)
		self.led(False)

		for i in range(len(pairs)):
			if pairs[i][0] == b and pairs[i][1] == l:
				self.pol = 'left' if i < 4 else 'right'
				self.num = i % 4

	def get(self):
		return GPIO.input(self.btnPin)

	def led(self, s):
		self.ledState = (True if s else False)
		GPIO.output(self.ledPin, self.ledState)

	def _callback(self, t):
		if GPIO.input(self.btnPin) and time() - self.lp > 0.35:
			self.clicked = True
			#print(self.pol + str(self.num))
			self.lp = time()
			# self.led(not self.ledState)
			# sleep(0.1)
			# self.led(not self.ledState)
			self.callback(self)

	def callback(self, btn):
		pass

	def __str__(self):
		return 'Btn: %s | Led: %s' % (self.btnPin, self.ledPin)

	def __del__(self):
		GPIO.remove_event_detect(self.btnPin)


class Desk:
	def __init__(self, p):
		self.pairs = p
		self.L = list()
		self.R = list()

		for i in range(4):
			self.L.append(Button(*p[i]))
			self.R.append(Button(*p[i + 4]))

	def leds(self, s):
		for i in range(4):
			self.L[i].led(s)
			self.R[i].led(s)

	def get(self, s):
		pos = s[:-1]
		num = int(s[-1])

		if pos == 'left':
			return self.L[num]
		if pos == 'right':
			return self.R[num]
		return None


pairs = [[2, 3], [14, 15], [22, 23], [24, 25], [6, 13], [12, 16], [20, 21], [19, 26]]
desk = Desk(pairs)


def test1():
	for i in deskL:
		i.led(True)
	input()
	for i in deskL:
		i.led(False)

	for i in deskR:
		i.led(True)
	input()
	for i in deskR:
		i.led(False)

	for i in deskL:
		i.led(True)
		input()
		i.led(False)

	for i in deskR:
		i.led(True)
		input()
		i.led(False)


def test2():
	target = deskR
	while True:
		for i in range(4):
			deskL[i].led(True)
			deskR[i].led(True)
			sleep(0.2)
		for i in range(4):
			deskL[i].led(False)
			deskR[i].led(False)


if __name__ == '__main__':
	try:
		input = raw_input
	except NameError:
		pass

	for i in deskL:
		print(i)
	for i in deskR:
		print(i)

	test1()
	test2()
