import sqlite3 as lite
from time import sleep
import GoogleScraper

#TODO LITE: get authors with potentially ambigous names 
#urls = GoogleScraper.scrape(title, results_per_page=100, number_pages=1)

con = lite.connect('name.db')

with con:
  cur = con.cursor()
  c = 0
  
  #TODO select only titles which were not already downloaded 
  cur.execute("SELECT id, title FROM articles;") 
  articles = cur.fetchall() 
  
  for article_id, title in articles:
    print("article_id=" + str(article_id) + " title=" + title)
    
    urls = GoogleScraper.scrape(title, results_per_page=100, number_pages=1)

    data = []

    for url in urls: 
      # We use INSERT or REPLACE to be sure an id will be returned 
      cur.execute("INSERT OR REPLACE INTO urls (url) VALUES(?)", [url])  
      url_id = cur.lastrowid
      data.append([article_id, url_id]) 
    
    cur.executemany("INSERT OR IGNORE INTO article_url (article_id, url_id) VALUES(?,?)", data)
    con.commit()
    
    c += 1
    print("--downloaded " + str(c) + "/" + str(len(articles)))
    sleep(10) 
  
  
  
    