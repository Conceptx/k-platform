from flask import Flask, render_template, url_for, request, redirect, session
from bcrypt import hashpw
from secure import *
from datetime import *
from os import urandom
from functools import wraps
import pymongo

app = Flask(__name__)
app.secret_key = urandom(3)
app.config['UPLOAD_FOLDER'] = "../static/uploads/"

try:
    client = pymongo.MongoClient("mongodb://kudziya:kudziya2018@ds119113.mlab.com:19113/kudziya")
    db = client['kudziya']


    #Global Variables
    password = ""


    def login_required(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if 'username' in session:
                return f(*args, **kwargs)
            else:
                return redirect(url_for('login'))

        return wrap


    @app.route('/' ,methods=('GET', 'POST'))
    @app.route('/kudziya/home',methods=('GET', 'POST'))
    @login_required
    def kudziya():
        keen.add_event("visits", {
                    "visit": str(datetime.now())
                    })
        
        query = db.Products.find({}, {"Ref#":"1", "Name":"1", "Category":"1", "Description":"1", "Price":"1", "Image":"1"})

        products = []

        for i in query:
            ref = i['Ref#']
            name = i['Name']
            category = i['Category']
            description = i['Description']
            price = i['Price']

            products.append((ref, name, category, description, price))

        if 'username' in session:
            username = session['username']
        
        return render_template('index.html', products = products, username=username)

    @app.route('/login', methods=('GET', 'POST'))
    def login():
        active='active'
        if request.method == 'POST':
            name = request.form.get('username')
            password = request.form.get('password')

            query = db.Customers.find({"Name":name}, {"Password":"1", "Role":"1"})

            for i in query:
                dbPassword = i['Password']
                dbRole = i['Role']
                
                if hashpw(password.encode('utf-8'), key) == bytes(dbPassword.encode('utf-8')) :
                    
                    keen.add_event("signins", {
                    "username": name
                    })
                    keen.add_event("visits", {
                    "visit": str(datetime.now())
                    })

                    session['username'] = name

                    if dbRole == 'admin':
                        return redirect(url_for('dashboard'))
                    else:
                        return redirect(url_for('kudziya'))    

        return render_template('signup.html', active=active)

    @app.route('/signup', methods=('GET', 'POST'))
    def signup():
        
        if request.method == 'POST':
            name = request.form.get('username')
            email = request.form.get('email')
            password = (hashpw(request.form.get('password').encode('utf-8'), key)).decode('utf-8')

            db.Customers.insert({"Name":name, "Email":email, "Password":password, "Role":"user"})

            keen.add_event("signups", {
            "username": name
            })
            keen.add_event("visits", {
                    "visit": str(datetime.now())
                    })

            return redirect(url_for('login'))
            
        return render_template('signup.html')

    @app.route('/logout')
    def logout():
        session.pop('username', None)
        return redirect(url_for('login'))

    @app.route('/dashboard',methods=('GET', 'POST'))
    @login_required
    def dashboard():
        query = db.Customers.find({"Role":"admin"}, {"Name":"1", "Password":"1", "Email":"1"})
        credentials = []
        global password

        for i in query:
            name = i['Name']
            email = i['Email']
            password = i['Password']

            credentials.extend((name, email))

        categories = []
        query = db.Categories.find({}, {"Category":"1"})

        for i in query:
            categories.append(i['Category'])

        # Products Count
        products = db.Products.count()

        # Visits
        visits = keen.count("visits", timeframe="this_30_days")
        
        # Kudziya Page Clicks Count
        clicks = keen.count("clicks", timeframe="this_30_days")

        # Registered User Count
        count = db.Customers.count({"Role":"user"})
        
        return render_template('dashboard.html', credentials=credentials, categories=categories, count=count,clicks=clicks, visits=visits, products=products)

    @app.route('/category',methods=('GET', 'POST'))
    @login_required
    def category():
        categories = []
        query = db.Categories.find({}, {"Category":"1", "Date Created":"1"})

        for i in query:
            categories.append((i['Category'], i['Date Created']))
        
        return render_template('categories.html', categories=categories)

    @app.route('/posts',methods=('GET', 'POST'))
    @login_required
    def posts():
        return render_template('posts.html')

    @app.route('/users',methods=('GET', 'POST'))
    @login_required
    def users():
        return render_template('users.html')

    @app.route('/invoices')
    @login_required
    def invoices():
        if 'username' in session:
            username = session['username']

        return render_template('invoice.html', username=username)

    @app.route('/mailbox')
    @login_required
    def mailbox():
        if 'username' in session:
            username = session['username']
            
        return render_template('mailbox.html', username=username)

    #Add Product
    @app.route('/add/products', methods=('GET', 'POST'))
    @login_required
    def addProduct():

        if request.method == 'POST':

            title = request.form.get('title')
            price = request.form.get('price')
            category = request.form.get('category')
            features = (request.form.get('description')).split('\r\n')
            file = request.files.get('image')
            
            name = request.form.get('filename')
            
            with open('product.jpg', 'wb') as img:
                img.write(bytes(file.read()))

            #Checking for file extension for image
            if name.endswith('.jpg') == True or name.endswith('.img') == True or name.endswith('.png') == True:
                count = db.Products.count()
                db.Products.insert({"Ref#":"PI" + str(count), "Name":title, "Price":price, "Category":category, "Description":features, "Image":bytes(file)})

            return redirect(url_for('posts'))

    #Add category
    @app.route('/add/category', methods=('GET', 'POST'))
    @login_required
    def addCategory():

        if request.method == 'POST':
            category = request.form.get('category')

            db.Categories.insert({"Category":category, "Date Created":str(date.today())})
            return redirect(url_for('category'))
            
    # Edit account settings
    @app.route('/edit/admin/account', methods=('GET', 'POST'))
    @login_required
    def editAdminAccount():

        if request.method == 'POST':
            name = request.form.get('username')
            email = request.form.get('email')
            oldpassword = request.form.get('oldpassword')
            newpassword = request.form.get('newpassword')

            if name == '' and email == '':
                pass
            elif name == '' and email != '':
                db.Customers.update({"Role":"admin"}, {"$set":{"Email":email}})
            elif email == '' and name !='':
                db.Customers.update({"Role":"admin"}, {"$set":{"Name":name}})
            else:
                db.Customers.update({"Role":"admin"}, {"$set":{"Name":name, "Email":email}})

            if oldpassword != '' and newpassword != '':
                if hashpw(oldpassword.encode('utf-8'), key) == bytes(password.encode('utf-8')):
                    db.Customers.update({"Role":"admin"}, {"$set":{"Password":(hashpw(newpassword.encode('utf-8'),key)).decode('utf-8')}})

            return redirect(url_for('login'))

except Exception:
    redirect(url_for('pageError'))

except pymongo.errors:
    redirect(url_for('pageError'))

@app.errorhandler(500)
def serverError(e):
    return render_template("500.html")

@app.route('/pageError')
def pageError():
    return render_template("500.html")

if __name__ == '__main__':

    app.run(host='0.0.0.0')

