# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MediaItem(scrapy.Item):
    pid = scrapy.Field()
    title = scrapy.Field()
    cover = scrapy.Field()
    description = scrapy.Field()
    duration = scrapy.Field()
    categories = scrapy.Field()
    keywords = scrapy.Field()
    media_1080_url = scrapy.Field()
    media_720_url = scrapy.Field()
    media_540_url = scrapy.Field()
    media_360_url = scrapy.Field()



class PostItem(scrapy.Item):
    pid = scrapy.Field()
    duration = scrapy.Field()
    thumbnail = scrapy.Field()
    title = scrapy.Field()
    preview = scrapy.Field()
    video = scrapy.Field()
    category = scrapy.Field()
    created_at = scrapy.Field()
    play_counts = scrapy.Field()
    like_counts = scrapy.Field()
    description = scrapy.Field()


class CommentItem(scrapy.Item):
    cid = scrapy.Field()
    banner = scrapy.Field()
    name = scrapy.Field()
    avatar = scrapy.Field()
    intro = scrapy.Field()
    like_counts = scrapy.Field()
    fans_counts = scrapy.Field()
    follow_counts = scrapy.Field()
    locations = scrapy.Field()
    career = scrapy.Field()


class ComposerItem(scrapy.Item):
    cid = scrapy.Field()
    banner = scrapy.Field()
    name = scrapy.Field()
    avatar = scrapy.Field()
    intro = scrapy.Field()
    like_counts = scrapy.Field()
    fans_counts = scrapy.Field()
    follow_counts = scrapy.Field()
    locations = scrapy.Field()
    career = scrapy.Field()


class CommentItem(scrapy.Item):
    commentid = scrapy.Field()
    pid = scrapy.Field()
    content = scrapy.Field()
    like_counts = scrapy.Field()
    created_at = scrapy.Field()
    cid = scrapy.Field()
    uname = scrapy.Field()
    avatar = scrapy.Field()
    reply = scrapy.Field()


class CopyrightItem(scrapy.Item):
    cid = scrapy.Field()
    pid = scrapy.Field()
    pcid = scrapy.Field()
    roles = scrapy.Field()


class XinpianchangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
