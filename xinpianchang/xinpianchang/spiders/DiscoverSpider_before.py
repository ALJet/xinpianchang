import scrapy
import json
from scrapy import Request
from xinpianchang.items import PostItem, CommentItem, ComposerItem, CopyrightItem, VideoItem
import re
import requests
import json
import time
import random


def my_strip(info):
    if info:
        return info.strip()
    return ''


cookies = {
    'Authorization': 'A26F51084B88500BF4B885427B4B8858B394B885B7E7169365C9'
}


def gen_session_id():
    return "".join(random.sample([chr(i) for i in range(97, 97 + 26)], 26))


def convert_int(s):
    if type(s) is str:
        return int(s.replace(",", ""))
    return 0


class DiscoverspiderSpider_before(scrapy.Spider):
    name = 'DiscoverSpiderBefore'
    allowed_domains = ['www.xinpianchang.com', 'mod-api.xinpianchang.com', 'app.xinpianchang.com']
    start_urls = ['https://www.xinpianchang.com/channel/index/sort-like/']

    page_count = 0

    # 提取作者的著作权信息
    composer_url = 'http://www.xinpianchang.com/u%s?from=articleList'

    def parse(self, response):
        # self.page_count += 1
        # if self.page_count >= 4:
        #     self.page_count = 0
        #     cookies.update(PHPSESSID=gen_session_id())

        post_list = response.xpath('//ul[@class="video-list"]/li')
        u_url = 'http://www.xinpianchang.com/a%s'
        for post in post_list:
            pid = post.xpath('./@data-articleid').extract_first()
            request = Request(u_url % pid, callback=self.parse_media_page)
            request.meta['pid'] = pid
            yield request
        # sleep_time = random.randint(3, 8)
        # time.sleep(sleep_time)
        # 提取下一页的链接
        next_page = 'https://www.xinpianchang.com' + response.xpath('//div[@class="page"]/a[last()]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse, cookies=cookies)

    def parse_media_page(self, response):
        pid = response.meta['pid']
        # 获取vid 网页中vid
        # vid = response.xpath('//a[@class="collection-star hollow-star"]/@data-vid').extract_first()
        vid = re.findall('vid = \"(\w+)\";', response.text)
        # 还需要appkey appkey 最关键
        appkey = re.findall('modeServerAppKey = \"(\w+)\";', response.text)
        url = 'https://mod-api.xinpianchang.com/mod/api/v2/media/%s?appKey=%s&extend='
        new_url = url % (vid[0], appkey[0])
        video_request = Request(new_url, callback=self.parse_media_json_api)
        yield video_request
        video_request.meta['pid'] = pid
        comm_url = 'https://app.xinpianchang.com/comments?resource_id=%s&type=article&page=1&per_page=24'
        comm_url = comm_url % pid
        request = Request(comm_url, callback=self.parse_comments_json_api)
        yield  request
        # 创作者
        # creator_url = response.xpath("//ul[@class='creator-list']/li/a/@href").extract()
        creator_url = response.xpath("//a[@class='name-wrap']/@href").extract()
        for creator in creator_url:
            # print('creator:' , creator)
            cid = creator[2:creator.index("?")]
            # print('cid:', cid)
            url = 'https://www.xinpianchang.com%s'
            request = response.follow(url % creator, callback=self.parse_composer)
            request.meta['dont_merge_cookies'] = True
            request.meta['cid'] = cid
            yield request



    def parse_media_json_api(self, response):
        try:
            re_json = json.loads(response.text.encode('utf-8'))
            media = VideoItem()
            # print('pid: ', response.meta['pid'])
            media['pid'] = response.meta['pid']
            media['title'] = re_json['data']['title']
            media['cover'] = re_json['data']['cover']
            media['description'] = re_json['data']['description']
            media['duration'] = re_json['data']['duration']
            categories = ','.join(re_json['data']['categories'])
            media['categories'] = categories
            keywords = ','.join(re_json['data']['keywords'])
            media['keywords'] = keywords
            media['media_1080_url'] = re_json['data']['resource']['progressive'][0]['url']
            media['media_720_url'] = re_json['data']['resource']['progressive'][1]['url']
            media['media_540_url'] = re_json['data']['resource']['progressive'][2]['url']
            # media['media_360_url'] = re_json['data']['resource']['progressive'][3]['url']
            yield media
        except json.JSONDecodeError:
            print('json编译出错或者Too Many Requests')

    def parse_comments_json_api(self, response):
        re_json = json.loads(response.text.encode('utf-8'))
        for c in re_json['data']['list']:
            if str(c).strip() != "":
                comment = CommentItem()
                comment["uname"] = c["userInfo"]["username"]
                comment["avatar"] = c["userInfo"]["avatar"]
                comment["uid"] = c["userInfo"]["id"]
                comment["comment_id"] = c["id"]
                comment["pid"] = c["resource_id"]
                comment["content"] = c["content"]
                comment["created_at"] = c["addtime"]
                comment["like_counts"] = c["count_approve"]
                if c["referid"]:
                    comment["referid"] = c["referid"]
                yield comment
        next_page = re_json['data']['next_page_url']
        if next_page:
            next_page = f"https://app.xinpianchang.com{next_page}"
            yield response.follow(next_page, self.parse_comments_json_api)
        yield comment

    # def parse_post(self, response):
    #     # 提取视频信息
    #     print('parse_post')
    #     post = PostItem()
    #     post['pid'] = response.meta['pid']
    #     duration = response.meta['duration']
    #     if duration:
    #         duration = [int(i) for i in duration.replace("'", "").split()]
    #         duration = duration[0] * 60 + duration[1]
    #     post['duration'] = duration
    #     # 缩略图，列表页小图
    #     post['thumbnail'] = response.meta['thumbnail']
    #     post['title'] = response.xpath('//div[@class="title-wrap"]/h3/text()')
    #     # 视频页的预览大图 (已经没有了)
    #     post['preview'] = response.xpath(
    #         '//div[@class="filmplay"]//img/@src').extract_first()
    #     # 没有了
    #     post['video'] = response.xpath('//video[@id="xpc_video"]/@src').get()
    #     cates = response.xpath('//span[@class="cate v-center"]/a/text()').extract()
    #     post['category'] = '-'.join([cate.strip() for cate in cates])
    #     # 发布时间
    #     post['created_at'] = response.xpath('//span[@class="update-time v-center"]/i/text()').get()
    #     # 播放次数
    #     post['play_counts'] = response.xpath('//i[contains(@class, "play-counts")]/text()').get().replace(",", "")
    #     # 点赞次数
    #     post['like_counts'] = response.xpath('//span[contains(@class, "like-counts")]/text()').get()
    #     # 描述
    #     desc = response.xpath('//p[contains(@class, "desc")]/text()').get()
    #     post['description'] = desc.strip() if desc else ''
    #     yield post

    # 解析创作者请求
    def parse_composer(self, response):
        banner, = re.findall("background-image:url\((.+?)\)",
                             response.xpath("//div[@class='banner-wrap']/@style").get())
        composer = ComposerItem()
        composer["banner"] = banner
        composer["cid"] = response.meta["cid"]
        composer["name"] = my_strip(response.xpath("//p[contains(@class,'creator-name')]/text()").get())
        composer["intro"] = my_strip(response.xpath("//p[contains(@class,'creator-desc')]/text()").get())
        composer["like_counts"] = convert_int(response.xpath("//span[contains(@class,'like-counts')]/text()").get())
        composer["fans_counts"] = convert_int(response.xpath("//span[contains(@class,'fans-counts')]/text()").get())
        composer["follow_counts"] = convert_int(
            response.xpath("//span[@class='follow-wrap']/span[contains(@class,'fw_600')]/text()").get())
        location = response.xpath("//span[contains(@class, 'icon-location')]/following-sibling::span[1]/text()").get()
        if location:
            composer["locations"] = location.replace("\xa0", "")
        else:
            composer["locations"] = ""
        composer["career"] = response.xpath(
            "//span[contains(@class, 'icon-career')]/following-sibling::span[1]/text()").get()
        yield composer

