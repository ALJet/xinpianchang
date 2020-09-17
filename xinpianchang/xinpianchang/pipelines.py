# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

import pymysql
from scrapy.exceptions import DropItem


class MysqlPipeline:
    def __init__(self):
        self.comment_set = set()
        self.composers_set = set()
        self.video_set = set()
        pass

    # 开始调用一次
    def open_spider(self, spider):
        self.conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            db='xinpianchang',
            user='root',
            password='123456',
            # charset='utf8',
            charset='utf8mb4'
        )
        self.cur = self.conn.cursor()

    # 关闭调用一次
    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()

    # 每产生一个调用一次
    def process_item(self, item, spider):
        # keys = item.keys()
        # values = list(item.values)   # 是一个元组-->集合
        self.check_repeat(item)
        keys, values = zip(*item.items())
        sql = "insert into {}({}) values({}) ON DUPLICATE KEY UPDATE {}".format(
            item.table_name,
            ','.join(keys),
            ','.join(['%s'] * len(keys)),
            ",".join(["`{}`=%s".format(key) for key in keys])
        )
        self.cur.execute(sql, values * 2)
        self.conn.commit()
        # 输出语句
        print(self.cur._last_executed)
        return item

    # 除去重复的数据
    def check_repeat(self, item):
        if (item.table_name == 'comment'):
            if item['comment_id'] in self.comment_set:
                raise DropItem("Duplicate comment found:%s" % item)
            else:
                self.comment_set.add(item['comment_id'])
        if (item.table_name == 'composers'):
            if item['cid'] in self.composers_set:
                raise DropItem("Duplicate composers found:%s" % item)
            else:
                self.composers_set.add(item['cid'])
        if (item.table_name == 'video'):
            if item['pid'] in self.video_set:
                raise DropItem("Duplicate video found:%s" % item)
            else:
                self.video_set.add(item['pid'])

# class XinpianchangPipeline:
#
#     def process_item(self, item, spider):
#         data = dict(item)
#         self.post.insert(data)
#         return item
