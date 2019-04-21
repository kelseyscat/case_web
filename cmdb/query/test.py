# -*- coding: UTF-8 -*-
import pymysql  # 导入 pymysql
import word_tagging
import string
import unicodedata

def C_trans_to_E(string):
    E_pun = u',.!?[]()<>"\''
    C_pun = u'，。！？【】（）《》“‘'
    table= {ord(f):ord(t) for f,t in zip(C_pun,E_pun)}
    return string.translate(table)
# 打开数据库连接
db = pymysql.connect(host="localhost", user="root",
                     password="123456", db="wechat", port=3306)
# 使用cursor()方法获取操作游标
cur = db.cursor()

# 1.查询操作
# 编写sql 查询语句  user 对应我的表名
sql = "select wechat_id , contents from KN_MF_WX_FRIEND_MSG_201708"
try:
    cur.execute(sql)  # 执行sql语句
    results = cur.fetchall()  # 获取查询的所有记录
    # 遍历结果
    table = {ord(f): ord(t) for f, t in zip(
        u'，。！？【】（）％＃＠＆１２３４５６７８９０',
        u',.!?[]()%#@&1234567890')}
    for row in results:
        id = row[0]
        msg = row[1]
        msg_length=len(msg)
        
        msg=msg.translate(table)
        print(msg)
        # msg.replace("？","?")
        if "[网页链接]" in msg or "<url>" in msg or "</url>" in msg or "<msg>" in msg or "</msg>" in msg or "<title>" in msg or "</title>" in msg or "<source>" in msg or "href" in msg or "http" in msg or "<totallen>" in msg:
            continue
        if ":" in msg and "[名片]" not in msg and "手机联系人" not in msg:
            n_pos = msg.index(':')
            id = msg[0:n_pos]
            msg=msg[n_pos+2:msg_length]
            msg.replace(":","")
        cnt = msg.count("@")
        while(cnt != 0):
            if "@" in msg and "?" in msg:
                i1 = msg.find('@')
                i2 = msg.find('?')
                # print(msg[i1:i2])
                msg.replace(msg[i1:i2], "")
            else:
                break
            cnt-=1
        print(id)
        print(msg)
        # for i in word_tagging.Tagger.get_word_objects(msg):
        #     print i.token, i.pos
except Exception as e:
    raise e
finally:
    db.close()  # 关闭连接
