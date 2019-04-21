# -*- coding: utf-8 -*-
import jena_sparql_endpoint
import question2sparql
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def searchMain(question):
    # 连接Fuseki服务器。
        fuseki = jena_sparql_endpoint.JenaFuseki()
    # 初始化自然语言到SPARQL查询的模块，参数是外部词典列表。
        q2s = question2sparql.Question2Sparql(['./cmdb/query/external_dict/drug_name.txt', './cmdb/query/external_dict/person_name.txt',
                                           './cmdb/query/external_dict/case_name.txt', './cmdb/query/external_dict/drug_to_person.txt'])
        my_query = q2s.get_sparql(question.decode('utf-8')) #sparql查询语句
        # print my_query
        if my_query is not None:
            result = fuseki.get_sparql_result(my_query)
            value = fuseki.get_sparql_result_value(result)
            # print value
            # 判断结果是否是布尔值，是布尔值则提问类型是"ASK"，回答“是”或者“不知道”。
            if isinstance(value, bool):
                if value is True:
                    # print 'Yes'
                    re='Yes:)'
                else:
                    # print 'I don\'t know. :('
                    re = 'I don\'t know. :('
            else:
                # 查询结果为空，根据OWA，回答“不知道”
                if len(value) == 0:
                    # print 'I don\'t know. :('
                    re = 'I don\'t know. :('
                elif len(value) == 1:
                    # print value[0]
                    re = value[0]
                else:
                    output = ''
                    for v in value:
                        output += v + u'、'
                    # print output[0:-1]
                    re = output[0:-1]
        else:
            # 自然语言问题无法匹配到已有的正则模板上，回答“无法理解”
            # print 'I can\'t understand. :('
            re = 'I can\'t understand. :('
        return re

if __name__ == '__main__':
    while(True):
        question = raw_input()
        re=searchMain(question)
        print re
        print '#' * 100