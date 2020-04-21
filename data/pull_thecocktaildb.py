import pprint
import requests
import re
import string

site = "https://www.thecocktaildb.com"

def get_drink_list():
    url = site + "/api/json/v1/1/list.php?s=list"
    payload = {}
    headers= {}
    response = requests.request("GET", url, headers=headers, data = payload)
    pprint.pprint(response.json())
    return response.json()['drinks']

def get_drink_detail(drink_name):
    url = site + "/api/json/v1/1/search.php?s=" + drink_name
    payload = {}
    headers= {}
    response = requests.request("GET", url, headers=headers, data = payload)
    return response.json()

def get_ingrediant_list():
    url = site + "/api/json/v1/1/list.php?i=list"
    payload = {}
    headers= {}
    response = requests.request("GET", url, headers=headers, data = payload)
    return response.json()['drinks']

def get_ingredient_details(ingredient_name):
    url = site + "/api/json/v1/1/search.php?i=" + ingredient_name
    payload = {}
    headers= {}
    response = requests.request("GET", url, headers=headers, data = payload)
    return response.json()


def slugify(text):
    text = text.lower()
    return re.sub(r'[\W_]+', '-', text)

def format_ingredients(i):
    i = i['ingredients'][0]
    abv = 0
    if 'strABV' in i:
        if i['strABV'] is not None:
            abv = int(i['strABV'])
    else:
        abv = 0

    return {slugify(i['strIngredient']): {
        'type': defaultValue(i, 'strType', None),
        'description': defaultValue(i, 'strDescription', ''),
        'abv': abv,
        'brandName': defaultValue(i, 'strIngredient', None),
        'image': '',
        'alternatives': [],
        'quality': { 'high': [], 'medium': [], 'low': [] }
   }}

def defaultValue(i, key, default=None):
    try:
        return i[key]
    except:
        return default

#def get_glasses_list():


#def get_glass_detail(glass_name):

#ingredients = get_ingrediant_list()
#ing = {}
#for i in ingredients:
  #detail = format_ingredients(get_ingredient_details(i['strIngredient1']))
  #for i in detail:
      #ing[i] = detail[i]
#pprint.pprint(ing)

drink = get_drink_list()
