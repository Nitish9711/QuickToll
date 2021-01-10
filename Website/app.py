import math
import random
from flask import Flask, escape, request, render_template, url_for, request, redirect, flash, session, jsonify
from datetime import datetime
from datetime import date 
import pymongo
import json
from flask_mail import Mail, Message
import os
from werkzeug.utils import secure_filename
import paypalrestsdk


app = Flask(__name__)
UPLOAD_FOLDER = 'images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.secret_key = 'asdsdfsdfs13sdf_df%&'

paypalrestsdk.configure({
    "mode": "sandbox",  
    "client_id": "AeFYj-IEKsOMvgwCUfuQ17nmQrDYRPZi1731-F2-qls3OMgUz9ecHltD8jzDaiJjoGXojcedpOKm770d",
    "client_secret": "EKNIboVSYKvTcMn82exQX6vXAw9Ic1K2q5V2IpRzeDeEsnf-U_gkJZhahYRYl2O4rTr58tDufwo6-29a"})


# myclient = pymongo.MongoClient("mongodb://localhost:27017/")
myclient = pymongo.MongoClient("mongodb+srv://nitish_kumar:1234567890@cluster0.xt7ds.mongodb.net/QuickToll?retryWrites=true&w=majority")


with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = True
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail-user'],
    MAIL_PASSWORD=params['gmail-password'],
    TEMPLATES_AUTO_RELOAD=True
)
mail = Mail(app)


def allowed_file(self, filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class utility:

    def check(self, vehicle_number):

        sd = store()
        doc = sd.user.find_one({"vehicle_number": vehicle_number})
        if doc == None:
            print("not found")
            return 0
        else:
            print("found")
            otp = self.generateOTP()
            self.send_otp_mail(otp, doc["email"])
            return otp

    def contact_mail(self, name, email, message, phone, date):
        msg = Message(
            'Contact US',
            sender=str(params['gmail-user']),
            recipients=[str(email)]
        )
       

        msg.body = 'Thanks For contacting Us We Will reach you soon.'
        mail.send(msg)

    def generateOTP(self):
        digits = "0123456789"
        OTP = ""
        for i in range(4):
            OTP += digits[math.floor(random.random() * 10)]

        return OTP

    def send_otp_mail(self, otp,email):
        msg = Message(
            'Your One time password for QuickToll is ',
            sender=str(params['gmail-user']),
            # recipients=['nitishk12c@gmail.com']
            recipients=[str(email)]
        )
        msg.body = otp
        mail.send(msg)

    def update_otp(self, otp, vehicle_number):
        sd = store()

        query = {"vehicle_number": vehicle_number}
        new_values = {"$set": {"otp": otp}}
        sd.user.update_one(query, new_values)

    def check_otp(self, otp, vehicle_number):
        sd = store()
        doc = sd.user.find_one({"vehicle_number": vehicle_number})
        if doc is None:
            return False
        else:
            if(doc["otp"] == str(otp)):
                return doc
            return False
    
    def payment_mail(self, vehicle_number,email,total):
        msg = Message(
            'Payment Mail',
            sender=str(params['gmail-user']),
            recipients=[str(email)]
        )
       
        msg.body = "Your tax Toll for vehicle Number " + (vehicle_number) + "on date" + str(date.today()) + "of amount" + str(total)
        mail.send(msg)
    
    


util = utility()


class store(utility):

    def __init__(self):
        # self.QuickToll = myclient["QuickToll"]
        self.QuickToll = myclient.get_database('QuickToll')
        self.contact = self.QuickToll["contact"]
        self.user = self.QuickToll["user"]

    def Contacts(self, name, phone_num, msg, date, email):
        post = {
            "name": str(name),
            "date": str(date),
            "email": str(email),
            "message": str(msg),
            "phone_num": str(phone_num),
            "otp": str("0")
        }
        self.contact.insert_one(post)
        self.contact_mail(name, email, msg, phone_num, date)

    def User(self, f_name, l_name, email, phone_num, address, city, state, zip, v_type, vehicle_number, date, image):
        post = {
            "first_name": str(f_name),
            "last_name": str(l_name),
            "date": str(date),
            "email": str(email),
            "phone_num": str(phone_num),
            "address": str(address),
            "city": str(city),
            "state": str(state),
            "zip": str(zip),
            "v_typ": str(v_type),
            "vehicle_number": str(vehicle_number),
            "total": int(0),
            # "tax": [""]
            
        }
        self.user.insert_one(post)

    def get_details(self, vehicle_number):
        doc = self.user.find_one({"vehicle_number": str(vehicle_number)})
        return doc


sd = store()


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        ob = store()
        ob.Contacts(name, phone, message, datetime.now(), email)
        return redirect(url_for('contact_thankyou'))

    return render_template('contact.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if(request.method == 'POST'):
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip')
        v_type = request.form.get('type')
        vehicle_number = request.form.get('vehicle_number')
        image = request.form.get('file1')
        ob = store()
        ob.User(first_name, last_name, email, phone, address, city,
                state, zip_code, v_type, vehicle_number, datetime.now(), image)
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        file1 = request.files['file1']
        path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
        file1.save(path)
        return redirect(url_for('thankyou'))

    return render_template('register.html')


@app.route('/thankyou', methods=['POST', 'GET'])
def thankyou():
    return render_template('thankyou.html')


@app.route('/contact_thankyou', methods=['POST', 'GET'])
def contact_thankyou():
    return render_template('contact_thankyou.html')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if "otp" in request.form:
            vehicle_number = request.form.get('vehicle_number')
            otp = util.check(vehicle_number)
            print(otp)
            if (otp != 0):
                util.update_otp(otp, vehicle_number)
                return ('', 204)
            elif (otp == 0):
                return render_template('wrong.html')

        elif "login" in request.form:
            vehicle_number = request.form.get('vehicle_number')
            otp_value = request.form.get('otp_value')
            doc = util.check_otp(otp_value, vehicle_number)
            if doc:
                session['vehicle_number'] = request.form['vehicle_number']
                return redirect(url_for('home'))

            return render_template('wrong_otp.html')

    login = False
    if 'vehicle_number' in session:
        login = True
    return render_template('index.html')


@app.route('/home', methods=['GET'])
def home():
    if 'vehicle_number' not in session:
        return render_template("404.html")

    vehicle_number = session['vehicle_number']
    print(vehicle_number)
    doc = sd.get_details(vehicle_number)
   
    return render_template('home.html', vehicle_number = vehicle_number , tax = doc["tax"], total = doc["total"] )


@app.route('/payment', methods=['POST'])
def payment():
    doc = sd.get_details(session["vehicle_number"])
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:3000/payment/execute",
            "cancel_url": "http://localhost:3000/"},
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "testitem",
                    "sku": "12345",
                    "price": str(doc["total"]),
                    "currency": "INR",
                    "quantity": 1}]},
            "amount": {
                "total": str(doc["total"]),
                "currency": "INR"},
            "description": "Toll Tax."}]})

    if payment.create():

        print('Payment success!')
        doc = sd.get_details(session["vehicle_number"])
        util.payment_mail(str(doc["vehicle_number"]),str(doc["email"]),str(doc["total"]))
        sd.user.update_one({"vehicle_number":doc["vehicle_number"]},{"$set":{"total": str(0)}} )
        
    else:
        print(payment.error)

    return jsonify({'paymentID' : payment.id})

@app.route('/execute', methods=['POST'])
def execute():
    success = False

    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    if payment.execute({'payer_id' : request.form['payerID']}):
       
     
        print('Execute success!')
        success = True

    else:
        print(payment.error)

    return jsonify({'success' : success})



@app.route('/logout')
def logout():
    session.pop('vehicle_number', None)
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.errorhandler(500)
def server_error(e):
    flash("OOPS! Something went wrong.. Please login again OR contact System Admin")
    return render_template('index.html')


app.run(debug=False)
