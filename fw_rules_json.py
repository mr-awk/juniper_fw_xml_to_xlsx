import json


with open("srx.json") as json_file:
    data = json.load(json_file)
    for p in data['address-book']:
        for a in data['global']:
            print (a['address'])