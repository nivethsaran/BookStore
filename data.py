import re
from urllib3.exceptions import InsecureRequestWarning
import warnings
import urllib3
import sqlite3
import json
import requests
import os
from bs4 import BeautifulSoup
warnings.simplefilter('ignore', InsecureRequestWarning)
ROOT_FOLDER = os.path.dirname(os.path.abspath(__file__))
bookstore = os.path.join(ROOT_FOLDER, 'bookstore.db')
conn = sqlite3.connect(bookstore)
url = "http://books.toscrape.com/"
page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')
sideCat = soup.find(class_="side_categories")
links=sideCat.findAll("a")[1:]
genrelist=[]
stock=5
for link in links:
    tempurl=url+link.get('href')
    temppage = requests.get(tempurl)
    tempsoup = BeautifulSoup(temppage.content, 'html.parser')
    rowSoup=tempsoup.find('ol',class_='row')
    genre = tempsoup.find('div', class_='page-header').find('h1').string
    genrelist.append(genre)
    olSoup=rowSoup.findAll(class_='product_pod')
    for bookSoup in olSoup:
        book=bookSoup.find('h3').find("a").get("title")
        price=bookSoup.find('p',class_="price_color").string[1:]
        ratingText=bookSoup.find('p',class_="star-rating")['class'][1]
        rating=0
        if(ratingText=="One"):
            rating=1
        elif(ratingText == "Two"):
            rating = 2
        elif(ratingText == "Three"):
            rating=3
        elif(ratingText == "Four"):
            rating=4
        elif(ratingText=="Five"):
            rating=5
        image = url + bookSoup.find('img')['src'][12:]
        details=url+'catalogue/'+ bookSoup.find('div',class_='image_container').find('a')['href'][9:]
        # print(image)
        dbURL = "INSERT INTO books values(?,?,?,?,?,?,?)"
        cursor = conn.cursor()
        cursor.execute(dbURL, (book,cursor.lastrowid,int(rating) ,float(price), image, details, genre))
        conn.commit()
    
print(genrelist)