# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class PhotoItem(Item):
    photo_id = Field()
    web_url = Field()
    name = Field()
    set_id = Field()
    set_name = Field()
    osize_url = Field()
    download_url = Field()


class PhotoSetItem(Item):
    set_id = Field()
    set_name = Field()
    photo_count = Field()

