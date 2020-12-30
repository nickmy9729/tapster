
recipe = {
    'name': 'Vesper',
    'ingredients': {
        'gin': 2,
        'oj': 4
    },
    'steps': [
        { 'pour': ['vermouth'] },
        { 'pour': ['gin', 'vodka'] },
        { 'manual_step': 'Strain into a chilled cocktail glass.' },
        { 'manual_step': 'Twist a slice of lemon peel over the drink, rub along the rim of the glass, and drop it in.' }
    ],
    'ice': 1, #more water volume needed
    'shaker_ice': 1, #some water added through melting
    'recommended_glass': 'martini'
}

glasses = {
    "solocup": {
        "size": 16 * 30,
        "picture": "./images/glasses/solocup.png"
    },
    "martini": {
        "size": round(float(8.8 * 30)),
        "picture": "./images/glasses/solocup.png"
    }
}

ingredients = {
    "oj": {
        "proof": 0,
        "abv": 0
    },
    "gin": {
        "proof": 80,
        "abv": 40
    },
    "vodka": {
        "proof": 80,
        "abv": 40
    },
    "vermouth": {
        "proof": 36,
        "abv": 18
    },
    "rum": {
        "proof": 80,
        "abv": 40
    },
    "spicedrum": {
        "proof": 80,
        "abv": 40
    },
    "malibu": {
        "proof": 42,
        "abv": 21
    },
    "whiskey": {
        "proof": 80,
        "abv": 40
    },
    "fireball": {
        "proof": 66,
        "abv": 33 
    }
}

cost_per_drink = "4.00"

def determineNumSTDDrinks(drink, totalvolume):
    totalgramAlcohol = 0
    for ingredient in drink['ingredients']:
        gramsperml = calculateAlcoholGrams(ingredient)
        

def dispenseByRecGlass(drink):
     glassMLS = glasses[drink['recommended_glass']]['size']
     if drink['ice']:
         glassMLS = round(float(glasses[drink['recommended_glass']]['size']) * .7)
     dispenseAmount(drink, glassMLS)

def dispenseAmount(drink, sizeML):
    smallest_ratio = 0
    for ingredient in drink['ingredients']:
        smallest_ratio =  smallest_ratio + (1 * drink['ingredients'][ingredient])
    multiple = sizeML / smallest_ratio
    for ingredient in drink['ingredients']:
        mls = round(drink['ingredients'][ingredient] * multiple)
        print(("ingredient " + ingredient + ": " + str(mls) + " ml"))

def calculateDrinkSize(drink, taste=0):
    standard_drink_grams = 14
    total_grams = 0
    for ingredient in drink['ingredients']:
        gramsperml = calculateAlcoholGrams(ingredient)
        ingredientgrams = gramsperml * drink['ingredients'][ingredient]
        total_grams = ingredientgrams + total_grams
    multiple = standard_drink_grams / total_grams
    if taste == 1:
      multiple = 1
    for ingredient in drink['ingredients']:
        mls = round(drink['ingredients'][ingredient] * multiple)
        print(("ingredient " + ingredient + ": " + str(mls) + " ml"))

def calculateAlcoholGrams(ingredient):
    grams = None
    if ingredient in ingredients:
        print(ingredient)
        volume = 1 #in milliliter
        abv = float(ingredients[ingredient]['abv']) / 100
        print(abv)
        grams = float(abv * .789)
        print(grams)
        return grams


calculateDrinkSize(recipe)
#dispenseAmount(recipe, 3785.41)
#dispenseByRecGlass(recipe)
