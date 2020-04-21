import pprint
import time
import sys
#import RPi.GPIO as GPIO
import json
import traceback
import threading

#import Adafruit_GPIO.SPI as SPI
#import Adafruit_SSD1306

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

#from dotstar import Adafruit_DotStar
from data.drinks import drink_list, drink_options
from data.glasses import glasses

#GPIO.setmode(GPIO.BCM)

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

LEFT_BTN_PIN = 13
LEFT_PIN_BOUNCE = 300

RIGHT_BTN_PIN = 5
RIGHT_PIN_BOUNCE = 300

OLED_RESET_PIN = 15
OLED_DC_PIN = 16

NUMBER_NEOPIXELS = 23
#I use other Pins here, Default is 26
NEOPIXEL_DATA_PIN = 21
#I use other Pins here, Default is 6
NEOPIXEL_CLOCK_PIN = 20
NEOPIXEL_BRIGHTNESS = 64

# Raspberry Pi pin configuration:
RST = 14
# Note the following are only used with SPI:
DC = 15
SPI_PORT = 0
SPI_DEVICE = 0

class MenuItem(object):
        def __init__(self, type, name, attributes = None, visible = True):
                self.type = type
                self.name = name
                self.attributes = attributes
                self.visible = visible

class Bartender: 
	def __init__(self):
		self.running = False

		# set the oled screen height
		self.screen_width = SCREEN_WIDTH
		self.screen_height = SCREEN_HEIGHT

		# configure screen
		spi_bus = 0
		spi_device = 0

		# Very important... This lets py-gaugette 'know' what pins to use in order to reset the display
		#self.led = disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000)) # Change rows & cols values depending on your display dimensions.
		
		# Initialize library.
		#self.led.begin()

		# Clear display.
		#self.led.clear()
		#self.led.display()


		# Create image buffer.
		# Make sure to create image with mode '1' for 1-bit color.
		self.image = Image.new('1', (self.screen_width, self.screen_height))

		# Load default font.
		self.font = ImageFont.truetype("FreeMono.ttf", 15)

		# Create drawing object.
		self.draw = ImageDraw.Draw(self.image)

		# load the pump configuration from file
		self.pump_configuration = Bartender.readPumpConfiguration()
		for pump in list(self.pump_configuration.keys()):
                        pass
			#GPIO.setup(self.pump_configuration[pump]["pin"], GPIO.OUT, initial=GPIO.HIGH)

		# setup pixels:
		self.numpixels = NUMBER_NEOPIXELS # Number of LEDs in strip

		# Here's how to control the strip from any two GPIO pins:
		datapin  = NEOPIXEL_DATA_PIN
		clockpin = NEOPIXEL_CLOCK_PIN
		#self.strip = Adafruit_DotStar(self.numpixels, datapin, clockpin)
		#self.strip.begin()           # Initialize pins for output
		#self.strip.setBrightness(NEOPIXEL_BRIGHTNESS) # Limit brightness to ~1/4 duty cycle

		# Set the Default or "StandBy Light" to Red in this case
		#for i in range(0, self.numpixels):
			#self.strip.setPixelColor(i, 0x00FF00)
		#self.strip.show() 

		print("Done initializing")

	@staticmethod
	def readPumpConfiguration():
		return json.load(open('data/pump_config.json'))

	@staticmethod
	def writePumpConfiguration(configuration):
		with open("data/pump_config.json", "w") as jsonFile:
			json.dump(configuration, jsonFile)

	def filterDrinks(self, menu):
            """
                Removes any drinks that can't be handled by the current pump configuration
            """
            drinks = []
            for d in drink_list:
                attributes = {}
                new_ingredients = {}
                ratio = list(d['ingredients'].values())
                print(ratio)
                my_gcd = self.calcGCD(ratio)
                for i in d['ingredients']:
                     d['ingredients'][i] = round(float(d['ingredients'][i] / my_gcd))
                for i in d:
                    attributes[i] = d[i]
                drinks.append(MenuItem('drink', d["name"], attributes))

            n = 0
            k = 0
            for drink in drinks:
                ingredients = 0
                num_ingredients = len(drink.attributes['ingredients'])
                for ingredient in drink.attributes["ingredients"]:
                    for pump in sorted(self.pump_configuration):
                        if self.pump_configuration[pump]['value'] == ingredient:
                            ingredients += 1
                if ingredients == num_ingredients:
                    drink.visible = True
            return drinks

	def calcGCD(self, my_list):
		result = my_list[0]
		for x in my_list[1:]:
			if result < x:
				temp = result
				result = x
				x = temp
			while x != 0:
				temp = x
				x = result % x
				result = temp
		return result 

	def dispenseByRecGlass(self, drink):
		glassMLS = glasses[drink['recommended_glass']]['size']
		if drink['ice']:
			glassMLS = round(float(glasses[drink['recommended_glass']]['size']) * .7)
		return dispenseAmount(drink, glassMLS)

	def dispenseAmount(self, drink, sizeML):
		smallest_ratio = 0
		ing = {}
		for ingredient in drink['ingredients']:
			smallest_ratio =  smallest_ratio + (1 * drink['ingredients'][ingredient])
		multiple = sizeML / smallest_ratio
		for ingredient in drink['ingredients']:
			mls = round(drink['ingredients'][ingredient] * multiple)
			ing[ingredient] = mls
		return ing

	def calculateDrinkSize(self, drink, taste=0):
		standard_drink_grams = 14
		total_grams = 0
		ing = {}
		for ingredient in drink['ingredients']:
			gramsperml = calculateAlcoholGrams(ingredient)
			ingredientgrams = gramsperml * drink['ingredients'][ingredient]
			total_grams = ingredientgrams + total_grams
		multiple = standard_drink_grams / total_grams
		if taste == 1:
			multiple = 1
		for ingredient in drink['ingredients']:
			mls = round(drink['ingredients'][ingredient] * multiple)
			ing[ingredient] = mls
		return ing

	def calculateAlcoholGrams(self, ingredient):
		grams = None
		if ingredient in ingredients:
			volume = 1 #in milliliter
			abv = float(ingredients[ingredient]['abv']) / 100
			grams = float(abv * .789)
			return grams

	def clean(self):
		waitTime = 20
		pumpThreads = []

		# cancel any button presses while the drink is being made
		# self.stopInterrupts()
		self.running = True

		for pump in list(self.pump_configuration.keys()):
			pump_t = threading.Thread(target=self.pour, args=(self.pump_configuration[pump]["pin"], waitTime))
			pumpThreads.append(pump_t)

		# start the pump threads
		for thread in pumpThreads:
			thread.start()

		# start the progress bar
		self.progressBar(waitTime)

		# wait for threads to finish
		for thread in pumpThreads:
			thread.join()

		# show the main menu
		self.menuContext.showMenu()

		# sleep for a couple seconds to make sure the interrupts don't get triggered
		time.sleep(2);


	def cycleLights(self):
		t = threading.currentThread()
		head  = 0               # Index of first 'on' pixel
		tail  = -10             # Index of last 'off' pixel
		color = 0xFF0000        # 'On' color (starts red)

		while getattr(t, "do_run", True):
			#self.strip.setPixelColor(head, color) # Turn on 'head' pixel
			#self.strip.setPixelColor(tail, 0)     # Turn off 'tail'
			#self.strip.show()                     # Refresh strip
			time.sleep(1.0 / 50)             # Pause 20 milliseconds (~50 fps)

			head += 1                        # Advance head position
			if(head >= self.numpixels):           # Off end of strip?
				head    = 0              # Reset to start
				color >>= 8              # Red->green->blue->black
				if(color == 0): color = 0xFF0000 # If black, reset to red

			tail += 1                        # Advance tail position
			if(tail >= self.numpixels): tail = 0  # Off end? Reset

	def lightsEndingSequence(self):
		# make lights green
		#for i in range(0, self.numpixels):
			#self.strip.setPixelColor(i, 0xFF0000)
		#self.strip.show()

		time.sleep(5)

		# set them back to red "StandBy Light"
		#for i in range(0, self.numpixels):
			#self.strip.setPixelColor(i, 0x00FF00)
		#self.strip.show() 

	def pour(self, pin, waitTime):
		pass
		#GPIO.output(pin, GPIO.LOW)
		time.sleep(waitTime)
		#GPIO.output(pin, GPIO.HIGH)
		# other way of dealing with Display delay, Thanks Yogesh

	def progressBar(self, waitTime):
		#-with the outcommented version, it updates faster, but there is a limit with the delay, you have to figure out-#
		#mWaitTime = waitTime - 7
		#interval = mWaitTime/ 100.0
		#if interval < 0.07:
		#	interval = 0
		#for x in range(1, 101):	
		interval = waitTime / 10.0
		for x in range(1, 11):
			#self.led.clear()
			self.draw.rectangle((0,0,self.screen_width,self.screen_height), outline=0, fill=0)
		#	self.updateProgressBar(x, y=35)
			self.updateProgressBar(x*10, y=35)
			#self.led.image(self.image)
			#self.led.display()
			time.sleep(interval)

        #
        # ingredients = {
        #        'vodka': 300,
        #        'oj': 200
        # }
	def pourIngredients(self, ingredients):
		# cancel any button presses while the drink is being made
		# self.stopInterrupts()
		self.running = True

		# launch a thread to control lighting
		#lightsThread = threading.Thread(target=self.cycleLights)
		#lightsThread.start()

		# Parse the drink ingredients and spawn threads for pumps
		maxTime = 0
		pumpThreads = []			
		for ing in list(ingredients):
			for pump in list(self.pump_configuration.keys()):
				if ing == self.pump_configuration[pump]["value"]:
					mlPMin = self.pump_configuration[pump]["flowrate"]
					waitTime = float(ingredients['ing'] / float(mlPMin / 60))
					if waitTime > maxTime:
						maxTime = waitTime
					pump_t = threading.Thread(target=self.pour, args=(self.pump_configuration[pump]["pin"], waitTime))
					pumpThreads.append(pump_t)
					
		# start the pump threads
		for thread in pumpThreads:
			thread.start()
		#Show in Console how long the Pumps running	
		print(("The pumps run for" ,maxTime,"seconds"))

		# wait for threads to finish
		for thread in pumpThreads:
			thread.join()

		# stop the light thread
		#lightsThread.do_run = False
		#lightsThread.join()
		
		# show the ending sequence lights
		#self.lightsEndingSequence()

		# sleep for a couple seconds to make sure the interrupts don't get triggered
		#time.sleep(2);

		# reenable interrupts
		# self.startInterrupts()
		self.running = False
