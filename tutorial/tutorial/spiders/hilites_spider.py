import scrapy


class HighlightsSpider(scrapy.Spider):
    name = "hilites"

    start_urls = [
        'https://blog.medium.com/welcome-to-the-medium-api-3418f956552',
        'https://theascent.biz/why-i-wake-up-at-6-am-f5911e54e6a4',
        'https://medium.com/the-mission/in-1995-this-astronomer-predicted-the-internets-greatest-failure-68a1c3927e46'
    ]
    #def start_requests(self):
    #    urls = [
    #        'http://quotes.toscrape.com/page/1/',
    #        'http://quotes.toscrape.com/page/2/',
    #    ]
    #    for url in urls:
    #        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = '-'.join(response.url.split('/')[3].split('-')[0:-1])
        filename = 'medium-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

