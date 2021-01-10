from ocr import extractnumber
from plate import plate_detector
import requests
import json
from datetime import date 
from pymongo import MongoClient
import pymongo
from pymongo.errors import *

try:
    # client = MongoClient('mongodb://localhost:27017/')
    myclient = pymongo.MongoClient("mongodb+srv://nitish_kumar:1234567890@cluster0.xt7ds.mongodb.net/QuickToll?retryWrites=true&w=majority")
except ConnectionFailure:
    print("Server not available")

from opencage.geocoder import OpenCageGeocode
from pprint import pprint
key = 'f17e3adbd2fc4d81ac431f466dfcbe87'
geocoder = OpenCageGeocode(key)


import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
with open("config.json") as json_data_file:
    data = json.load(json_data_file)

mymail = data["mail"]

sender_email = mymail["my_email"]

password = mymail["password"]
url = data["website"]

class utility:
    def coordinates(self):
        res = requests.get('https://ipinfo.io/')
        data = res.json()

        city = data['city']
        location = data['loc'].split(',')
        latitude = location[0]
        longitude = location[1]
        location = self.cal_loc(latitude, longitude)
        return location

    def cal_loc(self, latitude, longitude):        
        results = geocoder.reverse_geocode(latitude, longitude)
        data = results[0]
        district = data["components"]["state_district"]
        state = data["components"]["state"]

        location = district +", " +state 
        
        return location
    
    def send_mail(self, name,receiver_email, location, date, amount, total):
        
        message = MIMEMultipart("alternative")
        message["Subject"] = "Toll Tax"
        message["From"] = sender_email
        message["To"] = receiver_email
               
        text = """\
        """
        html = """\
        <html>
        <body>
                <h1>Toll Tax charge</h1><br>
            <h2> Hi, """ + name + """ </h2><br>
                <strong>Date </strong> : """ + date + """<br>
                <strong>Location </strong> : """ + location + """<br>
                <strong>Amount </strong> : """ + amount + """<br>
                
                <h4>Your Total Tax due is """ + total + """</h4><br>
                <h2> You can pay your due tax on <a href = """ + url + """ ><strong> QuickToll </strong></a> 
            
            </p>
        </body>
        </html>
        """
        

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)


        # Create secure connection with server and send email
        context = ssl.create_default_context()
        
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
        
            # Print any error messages to stdout
         



class toll(plate_detector, extractnumber, utility):
    def __init__(self, file_name):
        # self.quick_toll = client.QuickToll
        self.quick_toll = myclient.get_database('QuickToll')
        self.db = self.quick_toll["user"]
        self.file_name = file_name
        self.execute(file_name)
        self.update_toll()

    def execute(self, file_name):
        self.start_detection(file_name)
        self.start()

        print(str(self.get_number()))
        self.line = self.get_number()

    def update_toll(self):

        for doc in self.db.find():
            set_string1 = set(self.line)
            set_string2 = set(doc["vehicle_number"])
            matched_string = set_string1 & set_string2
            if (len(matched_string) >= 4):
                vehicle_type = doc["v_typ"]
                total = doc["total"]
                
                if vehicle_type == "Car":
                    total += 30
                    tax =30
                elif vehicle_type == "Truck":
                    total += 60
                    tax = 60
                elif vehicle_type == "Bus":
                    total += 70
                    tax = 70
                
                new_total = {"$set": {"total": total}}
                try:
                    self.db.update_one(
                        {"vehicle_number": doc["vehicle_number"]}, new_total)
                except:
                    print("document not found")
                    break

                today =  date.today()
                address = self.coordinates()
                query =  {"vehicle_number": doc["vehicle_number"]}
                values = [(str(today), str(address), str(tax))]
                name  = str(doc["first_name"] + doc["last_name"])
                               
                self.send_mail(name, doc["email"],str(address),str(today),str(tax),str(total))
               
                try:
                    old_values = doc["tax"]
                    print(old_values)
                    values = old_values + values
                    tax = {"$set": {"tax" : values}}
                    self.db.update_one(query, tax)
                except KeyError:
                    tax = {"$set":{"tax": values}}
                    self.db.update_one(query, tax)
                    

img = "1.jpg"
ob = toll(img)
