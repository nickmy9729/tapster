import pprint
import smbus
import time
import relay16

import sys
import os
import re
import json
import traceback
import threading

bus = smbus.SMBus(1)
address = 0x20
relayBoard = relay16.relay16(bus, address)
relayBoard.clearAllRelays()

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class MenuItem(object):
        def __init__(self, type, name, attributes = None, visible = True):
                self.type = type
                self.name = name
                self.attributes = attributes
                self.visible = visible

class Bartender: 
	def __init__(self):
		self.running = False

		# load the pump configuration from file
		self.pump_configuration = self.readPumpConfiguration()

		self.drink_list = self.getDrinkList()
		self.ingredients_list = self.getIngredientsList()
		self.glasses_list = self.getGlassesList()

		print("Done initializing")

	def slugify(self, text):
		text = text.lower()
		return re.sub(r'[\W_]+', '-', text)

	def getDrink(self, drink_name):
		path_to_json = './data/drinks/'
		json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
		for file in json_files:
			if file == drink_name + ".json":
				return self.readJsonFiles(path_to_json, [file])[0]

	def getIngredient(self, ing):
		path_to_json = 'data/ingredients/'
		json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
		for file in json_files:
			if file == ing + ".json":
				return self.readJsonFiles(path_to_json, [file])[0]

	def getDrinkList(self):
		path_to_json = './data/drinks/'
		json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
		return sorted(self.readJsonFiles(path_to_json, json_files), key=lambda k: k['name'])

	def readJsonFiles(self, path, files):
		data = []
		for file in files:
			if file == "sample.json":
				continue
			file = path + file
			print("Reading file: " + file)
			f = open(file,)
			data.append(json.load(f))
		return data

	def getGlassesList(self):
		path_to_json = './data/glasses/'
		json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
		return sorted(self.readJsonFiles(path_to_json, json_files), key=lambda k: k['name'])

	def getIngredientsList(self):
		path_to_json = 'data/ingredients/'
		json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
		return sorted(self.readJsonFiles(path_to_json, json_files), key=lambda k: k['name'])

	def readPumpConfiguration(self):
		return json.load(open('data/pump_config.json'))

	def getAllIngredients(self):
		pass


	def writePumpConfiguration(self, configuration):
		with open("data/pump_config.json", "w") as jsonFile:
			json.dump(configuration, jsonFile, indent=4)
		self.pump_configuration = self.readPumpConfiguration()

	def filterDrinks(self, menu):
		"""
		Removes any drinks that can't be handled by the current pump configuration
		"""
		drinks = []
		for d in self.drink_list:
			attributes = {}
			new_ingredients = {}
			ratio = list(d['ingredients'].values())
			my_gcd = self.calcGCD(ratio)
			for i in d['ingredients']:
				d['ingredients'][i] = round(float(d['ingredients'][i] / my_gcd))
			for i in d:
				attributes[i] = d[i]
			drinks.append(MenuItem('drink', d["name"], attributes))

		n = 0
		k = 0
		for drink in drinks:
			drink.visible = False
			ingredients = 0
			num_ingredients = len(drink.attributes['ingredients'])
			for ingredient in drink.attributes["ingredients"]:
				ing_data = self.getIngredient(ingredient)
				for pump in sorted(self.pump_configuration):
					if self.pump_configuration[pump]['value'] == ingredient or self.pump_configuration[pump]['value'] in ing_data['alternatives']:
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

	def mlToOZ(self, mls):
		return float(mls / 30)

	def ozToML(self, ounces):
		return float(ounces * 30)

	def calculateDrinkSize(self, drink, taste=0):
		standard_drink_grams = 14
		total_grams = 0
		ing = {}
		try:
			if 'recommended_size' in drink:
				return self.dispenseAmount(drink, self.ozToML(drink['recommended_size']))
		except:
			pass
		for ingredient in drink['ingredients']:
			gramsperml = self.calculateAlcoholGrams(ingredient)
			ingredientgrams = float(gramsperml * drink['ingredients'][ingredient])
			total_grams = ingredientgrams + total_grams
		if total_grams == 0:
			# Non Alcoholic Drink
			return self.dispenseAmount(drink, 414)
		multiple = standard_drink_grams / total_grams
		if taste == 1:
			multiple = 1
		for ingredient in drink['ingredients']:
			mls = round(drink['ingredients'][ingredient] * multiple)
			ing[ingredient] = mls
		return ing

	def calculateTotalDrinkSize(self, ing_size):
		total_size_mls = 0.0
		for i in ing_size:
			total_size_mls = float(total_size_mls) + float(ing_size[i])
		return total_size_mls

	def calculateAlcoholGrams(self, ingredient):
		grams = None
		try:
			element = list(map(lambda x: self.slugify(x['name']), self.ingredients_list)).index(ingredient)
			volume = 1 #in milliliter
			abv = float(self.ingredients_list[element]['abv']) / 100
			grams = float(abv * .789)
			return grams
		except ValueError:
			return 0

	def clean(self, pumps):
		waitTime = 20
		pumpThreads = []

		self.running = True

		for pump in list(self.pump_configuration.keys()):
			pump_t = threading.Thread(target=self.pour, args=(int(self.pump_configuration[pump]["pin"]), waitTime))
			pumpThreads.append(pump_t)

		# start the pump threads
		for thread in pumpThreads:
			thread.start()

		# wait for threads to finish
		for thread in pumpThreads:
			thread.join()

		# show the main menu
		self.menuContext.showMenu()

	def testPump(self, pump):
		p_cfg = self.pump_configuration[pump]
		self.pour(p_cfg['pin'], 3)

	def cleanPump(self, pump):
		p_cfg = self.pump_configuration[pump]
		self.primePump(pump)
		sleep(5 * 60)
		self.pour(p_cfg['pin'], 60)

	def primePump(self, pump):
		p_cfg = self.pump_configuration[pump]
		self.pour(p_cfg['pin'], 15)

	def pour(self, pin, waitTime):
		relayBoard.clearRelay(int(pin))
		relayBoard.setRelay(int(pin))
		time.sleep(waitTime)
		relayBoard.clearRelay(int(pin))

        # ingredients = {
        #        'vodka': 300,
        #        'oj': 200
        # }
	def pourIngredients(self, ingredients):
		# cancel any button presses while the drink is being made
		# self.stopInterrupts()
		self.running = True

		# Parse the drink ingredients and spawn threads for pumps
                # Example: {'cranberry-juice': 28, 'lime-juice': 14, 'soda': 142, 'vodka': 38}
		maxTime = 0
		pumpThreads = []			
		for ing in ingredients:
			ing_data = self.getIngredient(ing)
			for pump in list(self.pump_configuration.keys()):
				if ing == self.pump_configuration[pump]["value"] or self.pump_configuration[pump]["value"] in ing_data['alternatives']:
					mlPMin = float(self.pump_configuration[pump]["flowrate"])
					waitTime = float(float(ingredients[ing]) / float(mlPMin / 60))
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

		self.running = False
