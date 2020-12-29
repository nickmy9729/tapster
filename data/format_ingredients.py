
import pprint
import json
import re
from drinks import drink_list, drink_options

def slugify(text):
    text = text.lower()
    return re.sub(r'[\W_]+', '-', text)

new_list = {}
for i in drink_options:
    data = {
        "proof": 0,
        "abv": 0,
        "name": i['name'],
        "alternatives": [],
        "image": ""
    }

    f = open("./ingredients/" + slugify(i['name']) + ".json", "w")
    json.dump(data, f, indent=4, sort_keys=True)
    f.close()


pprint.pprint(new_list)
#print((json.dumps(new_list, indent=2)))
#print.pprint(new_list, width=1)
