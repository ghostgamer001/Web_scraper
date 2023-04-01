import requests
import csv
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime

# set up a dictionary with the URLs of the news sites
urls = {'New York Times': 'https://www.nytimes.com/',
        'CNN': 'https://www.cnn.com/',
        'BBC News': 'https://www.bbc.com/news',
        'The Guardian': 'https://www.theguardian.com/international',
        'Reuters': 'https://www.reuters.com/',
        'Al Jazeera': 'https://www.aljazeera.com/'}

# get the current date in the format DDMMYYYY
date = datetime.now().strftime("%d%m%Y")

# open the CSV file for writing
filename = f'{date}_verge.csv'
with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    # create a CSV writer object and write the header row
    writer = csv.writer(csvfile)
    writer.writerow(['id', 'URL', 'headline', 'author', 'date'])

    # connect to the SQLite database
    conn = sqlite3.connect('news.db')
    c = conn.cursor()

    # create a table in the database if it doesn't already exist
    c.execute('''CREATE TABLE IF NOT EXISTS articles 
                 (id INTEGER PRIMARY KEY, site TEXT, url TEXT, title TEXT, author TEXT, date TEXT)''')

    # loop over the news sites and scrape the articles
    for site, url in urls.items():
        # send a request to the site's homepage and get the response
        response = requests.get(url)

        # parse the HTML content of the response using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # find all the article links on the page
        links = soup.find_all('a', {'class': 'css-1wjnrbv'})

        # loop through the links and save the article information
        for i, link in enumerate(links):
            # extract the link URL, article title, author, and date
            article_url = link['href']
            article_title = link.text.strip()
            author_element = link.find_next('span', {'class': 'css-1nqbnmb'})
            article_author = author_element.text.strip() if author_element else ''
            date_element = link.find_next('time')
            article_date = date_element.get('datetime').split('T')[0] if date_element else ''

            # write the data to the CSV file
            writer.writerow([i+1, article_url, article_title, article_author, article_date])

            # insert the data into the SQLite database
            c.execute("INSERT INTO articles (id, site, url, title, author, date) VALUES (?, ?, ?, ?, ?, ?)",
                      (i+1, site, article_url, article_title, article_author, article_date))
    
    # commit the changes to the database and close the connection
    conn.commit()
    conn.close()

# print the contents of the CSV file
with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        print(row)


