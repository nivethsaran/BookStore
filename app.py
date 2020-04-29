import re
from urllib3.exceptions import InsecureRequestWarning
import warnings
from datetime import datetime, timedelta, timezone, date
import datetime
import time
import urllib3
import random
import os
from datautil import *
from flask import *
app = Flask(__name__)
import sqlite3,json
warnings.simplefilter('ignore', InsecureRequestWarning)
ROOT_FOLDER= os.path.dirname(os.path.abspath(__file__))
today = date.today()
app.config['SECRET_KEY'] = 'BookBasket'

@app.route('/')
def startup():
   message=''
   session['genre'] = 'All'
   if 'username' in session:
      message='Working'
   return render_template('startup.html',message=message)

#Login Route 
@app.route('/login', methods=('GET', 'POST'))
def login():
      error=''
      if request.method == 'POST':
         try:
            username = request.form['username']
            password = request.form['password']
            if len(username) == 0 or len(password) == 0:
               flash('Please fill both fields to login')
            else:
               conn = None
               try:
                  bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
                  conn = sqlite3.connect(bookstore)
                  dbURL = "SELECT username,password,fname,lname,email,mobile FROM user where username=?"
                  cursor = conn.cursor()
                  cursor.execute(dbURL,(username,))
                  rows=cursor.fetchall()
                  clen=int(len(rows))
                  if clen==0:
                     flash('Account does not exist')
                  else:
                     for row in rows:
                        if row[0]==username and row[1]==password:
                           fullname=row[2]+' '+row[3]
                           session['fullname']=fullname
                           session['username']=username
                           session['mobile']=row[5]
                           session['email']=row[4]
                           session['genre']='All'
                           return (redirect(url_for('home')))
                           
                        else:
                           flash('Wrong passwords')
                  
               except Exception as e:
                    print(e)
                    flash('Some unexpected error occured, so please try again')
               finally:
                  if conn:
                     conn.close()   
         except Exception as e:
             print(e)
             flash('Some unexpected error occured, so please try again')
      return render_template('login.html',genrelist=genrelist)
      
#Function to check is mobile number is valid
def isValidNumber(number):
    Pattern = re.compile("(0/91)?[5-9][0-9]{9}")
    return Pattern.match(number)

#Function to check if password is valid
def validPassword(password):
   flag = 0
   while True:
       if (len(password) < 8):
           flag = -1
           break
       elif not re.search("[a-z]", password):
           flag = -1
           break
       elif not re.search("[A-Z]", password):
           flag = -1
           break
       elif not re.search("[0-9]", password):
           flag = -1
           break
       elif not re.search("[_@$#]", password):
           flag = -1
           break
       elif re.search("\s", password):
           flag = -1
           break
       else:
           flag = 0
           return 'valid'

   if flag == -1:
       return 'invalid'

#Signup Route
@app.route('/signup',methods=['GET','POST'])
def signup():
   if request.method=='POST':
      fname=request.form['fname']
      lname=request.form['lname']
      username=request.form['username']
      password=request.form['password']
      email=request.form['email']
      mobile=request.form['mobile']
      regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
      if fname == '' or lname == '' or username == '' or password == '' or email == '' or mobile == '':
         flash('All fields are mandatory')
      elif not re.search(regex,email):
            flash('Enter Valid email')
      elif validPassword(password)=='invalid':
         flash('Weak Password')
      elif not isValidNumber(mobile):
         flash('Invalid Mobile Number')
      else:
         conn = None
         try:
            bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
            conn = sqlite3.connect(bookstore)
            dbURL = "INSERT INTO user values(?,?,?,?,?,?)"
            cursor = conn.cursor()
            cursor.execute(dbURL,(fname,lname,username,password,email,mobile))
            conn.commit()
            resp=make_response(redirect(url_for('login')))
            return resp
         except Exception as e:
            print(e)
            flash('Duplicate username')
         finally:
            if conn:
               conn.close()

   return render_template('signup.html',genrelist=genrelist)


#Home Route 
@app.route('/home',methods=["GET","POST"])
def home():
   listbm = []
   if 'username' in session:
      conn = None
      try:
         bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
         conn = sqlite3.connect(bookstore)
         dbURL = "SELECT * FROM books"
         cursor = conn.cursor()
         cursor.execute(dbURL)
         for row in cursor:
            listbm.append(row)
         random.shuffle(listbm)
         listbm=listbm[0:3]
      except Exception as e:
         print(e)
         print('hello')
      return render_template('home.html', listbm=listbm, genrelist=genrelist)
   else:
      return render_template('home.html', genrelist=genrelist)


@app.route('/cart', methods=["GET", "POST"])
def cart():
   cartlist = []
   price=0;
   bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
   conn = sqlite3.connect(bookstore)
   dbURL = "SELECT B.name,B.id,B.rating,B.price,B.image,B.details,B.genre,C.quantity from books as B,cart as C where C.id in (Select id from cart where username=?) and B.id==C.id"
   cursor = conn.cursor()
   cursor.execute(dbURL, (session['username'],))
   for row in cursor:
      cartlist.append(row)
      price+=row[7]*row[3]
   print(price)
   return render_template('cart.html', cartlist=cartlist, genrelist=genrelist,price=price)

@app.route('/catalouge', methods=["GET", "POST"])
def catalouge():
   booklist = []
   data={'currently':None}
   bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
   conn = sqlite3.connect(bookstore)
   if request.method=="POST":
      genre=request.form['genre']
      session['genre']=genre
      if(genre=='All'):
         dbURL = "SELECT * from books"
         cursor = conn.cursor()
         cursor.execute(dbURL)
      else:
         dbURL = "SELECT * from books where genre=?"
         cursor = conn.cursor()
         cursor.execute(dbURL,(genre,))
      for row in cursor:
         booklist.append(row)
      return render_template('catalouge.html', booklist=booklist, genrelist=genrelist)
   elif request.method=="GET":
      if('genre' in session):
         if(session['genre'] == 'All'):
            dbURL = "SELECT * from books"
            cursor = conn.cursor()
            cursor.execute(dbURL)
         else:
            dbURL = "SELECT * from books where genre=?"
            cursor = conn.cursor()
            cursor.execute(dbURL, (session['genre'],))
      else:
         dbURL = "SELECT * from books"
         cursor = conn.cursor()
         cursor.execute(dbURL)
      for row in cursor:
         booklist.append(row)
      return render_template('catalouge.html', booklist=booklist, genrelist=genrelist)
   return render_template('catalouge.html', genrelist=genrelist)


@app.route('/favourites', methods=["GET", "POST"])
def favourites():
   favlist = []
   bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
   conn = sqlite3.connect(bookstore)
   dbURL = "SELECT * from books where id in (Select id from fav where username=?)"
   cursor = conn.cursor()
   cursor.execute(dbURL,(session['username'],))
   for row in cursor:
      print(row)
      favlist.append(row)
   return render_template('favourites.html', favlist=favlist, genrelist=genrelist)



@app.route('/book/<int:bookno>', methods=["GET", "POST"])
def getbook(bookno):
   bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
   conn = sqlite3.connect(bookstore)
   dbURL = "select * from books where id=?"
   cursor = conn.cursor()
   cursor.execute(dbURL,(int(bookno),))
   bookdata=[]
   for row in cursor:
      bookdata=row
      break
   return render_template('book.html', bookdata=bookdata, genrelist=genrelist)

def getBookDetails(booknum):
   bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
   conn = sqlite3.connect(bookstore)
   dbURL = "select * from books where id=?"
   cursor = conn.cursor()
   cursor.execute(dbURL, (int(booknum),))
   bookdata = []
   for row in cursor:
      bookdata = row
   return row


@app.route('/addtocart/<int:bookno>', methods=["GET", "POST"])
def addtocart(bookno):
   bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
   conn = sqlite3.connect(bookstore)
   try:
      dbURL = "insert into cart values(?,?,1)"
      cursor = conn.cursor()
      cursor.execute(dbURL, (session['username'], int(bookno),))
      conn.commit()
   except Exception as e:
      print(e)
      flash('Already in cart')
      return redirect(url_for('catalouge'))
   flash("Added to Cart")
   return redirect(url_for('catalouge'))


@app.route('/updatecart/<int:bookno>', methods=["POST"])
def updateCart(bookno):
   print("Cehck")
   bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
   conn = sqlite3.connect(bookstore)
   if(request.method=="POST"):
      quantity=request.form['quantity']
      try:
         dbURL = "update cart set quantity=? where username=? and id=?"
         cursor = conn.cursor()
         cursor.execute(dbURL, (quantity,session['username'], int(bookno),))
         conn.commit()
      except Exception as e:
         print(e)
         flash('Already in cart')
         return redirect(url_for('cart'))
   flash("Added to Cart")
   return redirect(url_for('cart'))



@app.route('/removefromcart/<int:bookno>', methods=["GET", "POST"])
def removefromcart(bookno):
   bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
   conn = sqlite3.connect(bookstore)
   try:
      dbURL = "delete from cart where username=? and id=?"
      cursor = conn.cursor()
      cursor.execute(dbURL, (session['username'], int(bookno),))
      conn.commit()
   except Exception as e:
      print(e)
      flash(str(e))
      return redirect(url_for('cart'))
   flash("Removed from Cart")
   return redirect(url_for('cart'))


@app.route('/addtofav/<int:bookno>', methods=["GET", "POST"])
def addtofav(bookno):
   bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
   conn = sqlite3.connect(bookstore)
   try:
      dbURL = "insert into fav values(?,?)"
      cursor = conn.cursor()
      cursor.execute(dbURL, (session['username'],int(bookno),))
      conn.commit()
   except Exception as e:
      print(e)
      flash('Already in favourites')
      return redirect(url_for('catalouge'))
   flash("Added to Favourites")
   return redirect(url_for('catalouge'))


@app.route('/removefromfav/<int:bookno>', methods=["GET", "POST"])
def removefromfav(bookno):
   bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
   conn = sqlite3.connect(bookstore)
   try:
      dbURL = "delete from fav where username=? and id=?"
      cursor = conn.cursor()
      cursor.execute(dbURL, (session['username'], int(bookno),))
      conn.commit()
   except Exception as e:
      print(e)
      flash('Error')
      return redirect(url_for('favourites'))
   flash("Removed from Favourites")
   return redirect(url_for('favourites'))

@app.route('/orders')
def orders():
   return render_template('orders.html', genrelist=genrelist)


@app.route('/checkout')
def checkout():
   return render_template('checkout.html',genrelist=genrelist)

@app.route('/logout')
def logout():
   session.pop('username',None)
   session.pop('fullname',None)
   session.pop('mobile',None)
   session.pop('email',None)
   session.pop('genre',None)
   return render_template('login.html', genrelist=genrelist)




if __name__=='__main__':
    app.run(debug=True)
