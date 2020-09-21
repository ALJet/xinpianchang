import scrapy
import json
from scrapy import Request
from xinpianchang.items import PostItem, CommentItem, ComposerItem, CopyrightItem, VideoItem
import re
import requests
import json
import time
import random


class Before_DiscoverspiderSpider(scrapy.Spider):
    name = 'Before_DiscoverspiderSpider'
    allowed_domains = ['www.xinpianchang.com', 'mod-api.xinpianchang.com']
    start_urls = ['https://www.xinpianchang.com/channel/index/sort-like/']

    # 提取作者的著作权信息
    composer_url = 'http://www.xinpianchang.com/u%s?from=articleList'

    def parse(self, response):
        post_list = response.xpath('//ul[@class="video-list"]/li')
        u_url = 'http://www.xinpianchang.com/a%s'
        for post in post_list:
            pid = post.xpath('./@data-articleid').extract_first()
            request = Request(u_url % pid, callback=self.parse_media_page)
            yield request
        # sleep_time = random.randint(3, 8)
        # time.sleep(sleep_time)
        # 提取下一页的链接
        next_page = 'https://www.xinpianchang.com' + response.xpath('//div[@class="page"]/a[last()]/@href').get()
        print('next_page', next_page)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_media_page(self, response):
        # 获取vid 网页中vid
        # vid = response.xpath('//a[@class="collection-star hollow-star"]/@data-vid').extract_first()
        vid = re.findall('vid = \"(\w+)\";', response.text)
        # 还需要appkey appkey 最关键
        appkey = re.findall('modeServerAppKey = \"(\w+)\";', response.text)
        url = 'https://mod-api.xinpianchang.com/mod/api/v2/media/%s?appKey=%s&extend='
        new_url = url % (vid[0], appkey[0])
        request = Request(new_url, callback=self.parse_media_json_api)
        yield request
        # self.parse_media_api(new_url)

    def parse_media_json_api(self, response):
        try:
            re_json = json.loads(response.text.encode('utf-8'))
            print('media_api:', re_json)
            media = VideoItem()
            media['title'] = re_json['data']['title']
            media['cover'] = re_json['data']['cover']
            media['description'] = re_json['data']['description']
            media['duration'] = re_json['data']['duration']
            media['categories'] = re_json['data']['categories']
            media['keywords'] = re_json['data']['keywords']
            media['media_1080_url'] = re_json['data']['resource']['progressive'][0]['url']
            media['media_720_url'] = re_json['data']['resource']['progressive'][1]['url']
            media['media_540_url'] = re_json['data']['resource']['progressive'][2]['url']
            # media['media_360_url'] = re_json['data']['resource']['progressive'][3]['url']
            print('title:', media['title'])
            yield media
        except json.JSONDecodeError:
            print('json编译出错或者Too Many Requests')

    def parse_post(self, response):
        # 提取视频信息
        print('parse_post')
        post = PostItem()
        post['pid'] = response.meta['pid']
        duration = response.meta['duration']
        if duration:
            duration = [int(i) for i in duration.replace("'", "").split()]
            duration = duration[0] * 60 + duration[1]
        post['duration'] = duration
        # 缩略图，列表页小图
        post['thumbnail'] = response.meta['thumbnail']
        post['title'] = response.xpath('//div[@class="title-wrap"]/h3/text()')
        # 视频页的预览大图 (已经没有了)
        post['preview'] = response.xpath(
            '//div[@class="filmplay"]//img/@src').extract_first()
        # 没有了
        post['video'] = response.xpath('//video[@id="xpc_video"]/@src').get()
        cates = response.xpath('//span[@class="cate v-center"]/a/text()').extract()
        post['category'] = '-'.join([cate.strip() for cate in cates])
        # 发布时间
        post['created_at'] = response.xpath('//span[@class="update-time v-center"]/i/text()').get()
        # 播放次数
        post['play_counts'] = response.xpath('//i[contains(@class, "play-counts")]/text()').get().replace(",", "")
        # 点赞次数
        post['like_counts'] = response.xpath('//span[contains(@class, "like-counts")]/text()').get()
        # 描述
        desc = response.xpath('//p[contains(@class, "desc")]/text()').get()
        post['description'] = desc.strip() if desc else ''
        yield post
