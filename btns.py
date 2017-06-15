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
				self.pos = 'L' if i < 4 else 'R'
				self.num = i % 4

	def get(self):
		return GPIO.input(self.btnPin)

	def led(self, s):
		self.ledState = (True if s else False)
		GPIO.output(self.ledPin, self.ledState)

	def _callback(self, t):
		if GPIO.input(self.btnPin) and time() - self.lp > 0.35:
			self.clicked = True
			self.lp = time()
			self.callback(self)

	def callback(self, btn):    
		#print(self.pol + str(self.num))
		print(btn)

	def __str__(self):
		return '%s%s' % (self.pos, self.num)
		#return 'Btn: %s | Led: %s' % (self.btnPin, self.ledPin)

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

		if pos == 'L':
			return self.L[num]
		if pos == 'R':
			return self.R[num]
		print('Not button: '+str(s))
		return None


pairs = [[7, 8], [14, 15], [22, 23], [24, 25], [6, 13], [12, 16], [20, 21], [19, 26]]
desk = Desk(pairs)


def test1():
	for i in desk.L:
		i.led(True)
	print("L")
	input()
	desk.leds(False)

	for i in desk.R:
		i.led(True)
	print("R")
	input()
	desk.leds(False)

	for i in desk.L:
		i.led(True)
		print(i)
		input()
		i.led(False)

	for i in desk.R:
		i.led(True)
		print(i)
		input()
		i.led(False)

	print("All")
	desk.leds(True)
	input()
	


def test2():
	print("Rainbow")
	while True:
		for i in range(4):
			desk.L[i].led(True)
			desk.R[i].led(True)
			sleep(0.2)
		for i in range(4):
			desk.L[i].led(False)
			desk.R[i].led(False)


if __name__ == '__main__':
	try:
		input = raw_input
	except NameError:
		pass

	for i in desk.L:
		print(i)
	for i in desk.R:
		print(i)

	test1()
	test2()
