import scrapy
from datetime import datetime as dt


class MediumUrlSpider(scrapy.Spider):
    name = "medium_url_spider"
    start_urls = ['https://medium.com/browse/top/']
    today_used = False

    def parse(self, response):
        # find all article posts on page (normally 20)
        articles = response.css('.streamItem-cardInner--bmPostPreview')

        # scrape and format date
        try:
            datetext = response.css('.homeContainer-headerDescription::text').extract()
            datestr = datetext[0].split()[-3:]
            datestr[0] = datestr[0][0:3]
            date = dt.strptime(' '.join(datestr),'%b %d, %Y')
            dateprint = str(date).split()[0]
        except:
            #if today_used == False:
            dateprint = dt.today().strftime('%Y-%m-%d')
            #    today_used = True
            #else:
            #    raise

        # find, extract, and save each link from each article post
        filename = 'medium_urls_dates.txt'
        with open(filename,'a+') as f:
            for article in articles:
                url = article.css('a::attr(href)').extract()[-1].split('?')[0]
                f.write(url + ',' + dateprint + '\n')

        # find link to next page and follow
        next_page = response.css('.homeContainer-topStoriesNav')[0].css('a::attr(href)')[0].extract()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

