
import pprint
import json
from drinks import drink_list, drink_options


new_list = {}
for i in drink_options:
    new_list[i['value']] = {
        "proof": 0,
        "abv": 0,
        "name": i['name'],
        "quality": {
            "high": [],
            "medium": [],
            "low": []
        },
        "alternatives": [],
        "image": ""
    }

print(new_list)
#print((json.dumps(new_list, indent=2)))
#print.pprint(new_list, width=1)
