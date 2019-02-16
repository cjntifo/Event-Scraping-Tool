import os
import meetup.api
import json, csv
import requests
import datetime
import urllib
from datetime import datetime
from datetime import timedelta
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

#---------------------
# Function Definitions
#---------------------

def getEventFromURL(url_path, params):
    responseString = ""
    
    #params = {}
    r = requests.get(url_path, params=params)
    print("The server responded with status code: " + str(r.status_code))
    
    #print(r.url)
    responseString = r.text
    return responseString

def getApiKeyFromFile(keyfilePath):
    key = ""
    f = open(keyPath, 'r')
    key = f.read()
    return key

def decodeMeetupJSON(json_string):
    j = json.loads(json_string)
    i = 0
    
    results = j["results"]
    
    while i < len(results):
        event = results[i]
        print("Event no. " + str(i))
        print("Event name: " + event["name"])
        print("Event URL: " + event["event_url"])
        
        i += 1
    return json_string

def decodeOutSavvyJSON(json_string):
    j = json.loads(json_string)
    i = 0
    
    results = j["events"]
    
    while i < len(results):
        event = results[i]
        print("Event no. " +str(i))
        print("Event name: " + event["name"])
        print("Event URL: " + event["url"])
        
        i += 1
    return json_string

def outputCSV(m_json_string, os_json_string):
    
    filePath = open('Events.csv', 'w', encoding="utf-8")
    io = csv.writer(filePath, lineterminator='\n')
    
    io.writerow(["Event Name", "Event URL", "Event Start Date" ,"Venue Name", "Address_1", "Address_2", "Price info"])
    #name, url, start time, location, categories
    
    j = json.loads(m_json_string)
    print(str(j["meta"]["count"]) + " Meetup Events have been loaded.")
    for x in j["results"]:
        #print(x["venue"])
        informationList = [x["name"],
                            x["event_url"],
                            convertTime(x["time"])] 
        
        if 'price' in x:
            informationList.append(x["price"])
        else:
            informationList.append("")
        
        
        if 'venue' in x:
            if 'name' in x["venue"]:
                informationList.append(x["venue"]["name"])
                if 'address_1' in x["venue"]:
                    informationList.append(x["venue"]["address_1"])
                    if 'address_2' in x["venue"]:
                        informationList.append(x["venue"]["address_2"])
                    else:
                        informationList.append("")
                else:
                        informationList.append("")
            else:
                        informationList.append("")
        
        if 'price' in x:
            informationList.append(x["price"])
        else:
            informationList.append("")
            
        io.writerow(informationList)   
        
        
    j = json.loads(os_json_string)
    print(str(j["paging"]["page_size"]) + " OutSavvy Events have been loaded.")
    for x in j["events"]:
        informationList = [x["name"],
                            x["url"],
                            x["dates"][0]["startlocal"],
                            x["location_name"]]        
        
        informationList.append("")
        informationList.append("")
        
        #get pricing info
        os_event_price_info = getEventFromURL(os_url_path + "events/" + str(x["id"]) + "/tickettypes/", {'token': os_api_key})
        p = json.loads(os_event_price_info)
        
        for y in p["tickets"]:
            if y["status"] == "on_sale":
                if y["ticket_type"] == "free":
                    informationList.append("[Free]" + y["name"])
                elif y["ticket_type"] == "paid":
                    informationList.append("[Paid] " + y["name"] + " ticket: " + y["price"]["price_display"])
                elif y["ticket_type"] == "donation":
                    informationList.append("[Donation] " + y["name"] + " ticket: " + y["price"]["price_display"])
            else:
                informationList.append("[N/A] \"" + y["name"] + "\" ticket is " + y["status"])
        
        io.writerow(informationList)
    
    filePath.close()
    
def downloadMeetupImages(json_string):
    j = json.loads(json_string)
    if not os.path.exists("Images"):
        os.makedirs("Images")
    
    for x in j["results"]:
        if 'photo_url' in x:
            urllib.request.urlretrieve(x["photo_url"], "Images/" + validateFileName(x["name"]) + ".jpg")
            print("Image retrieved for for: " + x["name"])
        else:
            #use stock image
            continue
            
def downloadOutSavvyImages(json_string):
    j = json.loads(json_string)
    if not os.path.exists("SQUADImages"):
        os.makedirs("SQUADImages")
        
    #for filename in os.listdir():
        #os.unlink(filename)
    
    for x in j["events"]:
        if 'image_url' in x:
            urllib.request.urlretrieve(x["image_url"], "Images/" + validateFileName(x["name"]) + ".jpg")
            print("Retrieving image for: " + x["name"])
        else:
            #use stock image
            continue
            
def validateFileName(name):
    validName = ""
    for c in name:
        # Windows Filenames cannot include ... / \ : * ? " <> |
        if c != '.' and c != '/' and c != '\\' and c != ':' and c != '*' and c != '?' and c!= '"' and c != '<' and c != '>' and c != '|':
            validName += c
            
    return validName

def convertTime(time):
    return datetime.fromtimestamp(time/1000).strftime('%Y-%m-%d %H:%M:%S')
            

print("Welcome to Carl's data scraping script...")
    
#------------------
# Meetup setup (m_)
#------------------

m_client = meetup.api.Client('#') #Insert API Key

m_url_path = "https://api.meetup.com/2/"
m_api_key = "#" #Insert API Key

#---------------------
# OutSavvy Setup (os_)
#---------------------

os_url_path = "http://api.outsavvy.com/v1/"
os_api_key = "#" #Insert API Key

#--------------
# Fetch Events
#--------------

# Returns a meetupObject of events
#meetupObj_events = m_client.GetOpenEvents({'country':'GB', 'city':'London', 'category':'12', 'radius':'10'})

m_params = {
    'and_text': 'False',
    'country': 'gb',
    'offset': '0',
    'city': 'London',
    'format': 'json',
    'limited_events': 'False',
    'photo-host': 'public',
    'page': '100',
    'radius': '10',
    'category': '1',   #Retreieve events for a specific meetup category
    'desc': 'False',
    'time': ',14d',     #obtain events between NOW and 14 days
    'status': 'upcoming',
    'key': m_api_key
}
m_events = getEventFromURL(m_url_path + "open_events?", m_params)

os_params = {
    'page_size': '25', 
    'token': os_api_key
}
# Returns a JSON string with OutSavvy Events
os_events = getEventFromURL(os_url_path + "events/search/", os_params) 

#print(m_events)
#print(os_events)

print("Outputting CSV File...")
outputCSV(m_events, os_events)

print("Beginning image downloads...")
downloadMeetupImages(m_events)
downloadOutSavvyImages(os_events)

print("======================================")
print("Script running has terminated...")
print("======================================")