import json
import requests
import googlemaps
from datetime import datetime
import gmaps
from IPython.display import display
from flask import Flask, render_template, request


CACHE_FILENAME = 'cache.json'

api_key = 'DGogIvHeS9W5_tLdv5-60YTvO6M_431gBRHMYWTbHx6zgTr0TXI5pF_wQ08RfP6xetG1FJdED12gp0j7OzrCL0-Y8JVPREvPhxkY9XInXA3hpma99lWeNmGWR0qaY3Yx'
GOOGLE_API_KEY = 'AIzaSyAdmrBeRN-JSJQCWowHhrh4kT6KxussA90'

url = f'https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_API_KEY}'
data = {
    'considerIp': True, 
}

result = requests.post(url, data)

print(result.text)
result2 = json.loads(result.text)

# lat = 42.2903808
# lng = -83.6861952


lat = result2["location"]["lat"] 
lng = result2["location"]["lng"]


cache_dict = {}
def open_cache():
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 
  
class Yelp():
    def __init__(self, name = None, categories = None, rating = None, url = None, price = None, image_url = None, json = None):
        if json is None:
            self.name = name
            self.categories = categories
            self.rating= rating
            self.url = url
            self.price = price
            self.image_url = image_url
        else:                
            self.name = json['name']
            self.categories = json['categories'][0]['alias']
            self.rating = json['rating']
            self.url = json['url']
            if 'price' not in json.keys():
                self.price = None
            else:
                self.price = json['price']
            self.image_url = json['image_url']
    def info(self):
        return f"{self.name}, rating: {self.rating}"
    def urllink(self):
        return f"{self.url}"
    def makeDict(self):
        return {
            'name': self.name,
            'rating': self.rating,
            'url': self.url,
            'price': self.price,
            'image_url': self.image_url
        }

test = []
def getDict(List):
    dictList =[]
    testList = []
    for i in List["businesses"]:
        try:
            if i["rating"] >= 4.0:
                dictList.append(Yelp(json=i).makeDict())
                # urllist.append(Yelp(json=i).urllink())
        except:
            test.append(Yelp(json=i).info())
            testList.append(Yelp(json=i).makeDict())
    return dictList

def treePrice(List):
    priceTree = {'$': [], '$$': [], '$$$': [], '$$$$': []}
    priceTreefour = []

    for i in List["businesses"]:
        try:
            if i["price"] == "$":
                priceTree['$'].append(Yelp(json=i).info())
            elif i["price"] == "$$":
                priceTree['$$'].append(Yelp(json=i).info())
            elif i["price"] == "$$$":
                priceTree['$$$'].append(Yelp(json=i).info())
            elif i["price"] == "$$$$":
                priceTree['$$$$'].append(Yelp(json=i).info())
        except:
            priceTreefour.append(Yelp(json=i).info())
    print(priceTree)
    return priceTree
        
##Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['POST'])
def result():
    search_term = request.form["search_term"]
   
    if search_term == "exit":
        return render_template('noresult.html')

    elif request.form.get("Go") == "Go":
        headers = {'Authorization': 'Bearer %s' % api_key}
        params = {'term':'dinner', 'limit':'10', 'latitude':lat, 'longitude':lng}
        url='https://api.yelp.com/v3/businesses/search'
        response = requests.get(url, params=params, headers=headers).json()

        final = []
        finalale = getDict(response)
        for i in range(10):
            final.append([finalale[i]['name'], finalale[i]['price'], finalale[i]['rating'], finalale[i]['image_url'] ,finalale[i]['url']])
        
        return render_template('result.html', final=final)

    else:
        headers = {'Authorization': 'Bearer %s' % api_key}
        params = {'term':'dinner', 'limit':'10', 'location':search_term}
        url='https://api.yelp.com/v3/businesses/search'
        if search_term in cache_dict.keys():
            response = cache_dict[search_term]
            print("Result fetching from cache")
        else:
            response = requests.get(url, params=params, headers=headers).json()
            cache_dict[search_term] = response
            save_cache(cache_dict)
            print("Result fetching from api")

        final = []
        finalale = getDict(response)
        for i in range(10):
            final.append([finalale[i]['name'], finalale[i]['price'], finalale[i]['rating'], finalale[i]['image_url'] ,finalale[i]['url']])
        
        return render_template('result.html', final=final)

if __name__ == "__main__":
    cache_dict = open_cache()
    app.run(debug=True, use_reloader=False)