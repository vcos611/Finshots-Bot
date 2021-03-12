"""This script when run will extract article links from the Finshots website
 and update the links table in database"""

import datetime
import os

import mysql.connector as mc
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

print('updating database with fresh articles...')

# making the connection to database
load_dotenv()
User = os.getenv('DB_USER')
Host = os.getenv('DB_HOST')
Password = os.getenv('DB_PASSWORD')
Database = os.getenv('DB_DATABASE')

db = mc.connect(
    user=User,
    host=Host,
    password=Password,
    database=Database,
    autocommit=True
)
cur = db.cursor()

category = {
    "https://finshots.in/archive": "daily",
    "https://finshots.in/brief/": "brief",
    "https://finshots.in/markets/": "markets",
    "https://finshots.in/infographic/": "infographics"
}

# inserting data for each category
for url in category:

    # fetching source code of the link
    r = requests.get(url).content

    soup = BeautifulSoup(r, 'html.parser')
    div = soup.find('div', class_='post-feed')
    articles = div.find_all('article')

    for item in articles:
        # scrapping the data
        article = {
            'title': item.find('img')['alt'],
            'link_date': item.find('time')['datetime']
        }
        if category[url] == 'infographics':
            article['link'] = item.find('img')['src']
        else:
            article['link'] = "https://finshots.in" + item.find('a')['href']

        now = datetime.datetime.now().strftime(r"%Y:%m:%d %H:%M:%S")

        # updating links into articles table
        try:
            sql = ("insert into articles values(%s,%s,%s, %s, %s);")
            val = (article['link'], article['title'],
                   category[url], article['link_date'], now)
            cur.execute(sql, val)
            db.commit()

        except (mc.errors.IntegrityError, mc.errors.ProgrammingError):
            pass

# closing connection to the database
cur.close()
db.close()

print('success! database updated with latest articles!')
