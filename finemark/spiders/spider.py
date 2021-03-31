import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import FinemarkItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class FinemarkSpider(scrapy.Spider):
	name = 'finemark'
	start_urls = ['https://www.finemarkbank.com/about/news/']

	def parse(self, response):
		post_links = response.xpath('//a[@class="btn-block read-more"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//ul[@class="pagination-links"]/li[@class="last"]/a/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)

	def parse_post(self, response):
		try:
			date = response.xpath('//div[@class="post-info-line"]/div[@class="date"]//text()[not (ancestor::strong)][last()]').get().strip()
		except AttributeError:
			date = "None"
		title = response.xpath('//h1/text()').get()
		content = response.xpath('//div[@class="post-center"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=FinemarkItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
