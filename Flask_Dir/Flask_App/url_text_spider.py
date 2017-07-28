'''this is a python scraper. given a url, it will grab relevant information about the article and return a db row'''

import scrapy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd

class URLTextSpider(scrapy.Spider):
    name = "url_text_spider"

    def __init__(self, in_url=None, user=None, db=None):
        scrapy.Spider.__init__(self)
        self.the_url = in_url
        self.user = user
        self.db = db
        self.engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))

    	## create a database (if it doesn't exist)
    	if not database_exists(engine.url):
        	create_database(engine.url)

    def start_requests(self):
        urls = [
            self.the_url
        ]
        for a_url in urls:
            yield scrapy.Request(url=a_url, callback=self.parse)

    def parse(self, response):
        # find all article posts on page (normally 20)
        articles = response.css('.streamItem-cardInner--bmPostPreview')

        # find, extract, and save each link from each article post
        filename = 'medium_urls_dates.txt'
        with open(filename,'a+') as f:
            for article in articles:
                url = article.css('a::attr(href)').extract()[-1].split('?')[0]
                f.write(url + ',' + dateprint + '\n')