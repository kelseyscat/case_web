# encoding=utf-8

"""

@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: jena_sparql_endpoint.py

@time: 2017/12/20 17:42

@desc:
把从mysql导出的csv文件按照jieba外部词典的格式转为txt文件。
nz代表专名，本demo主要指电影名称。
nr代表人名。

"""
import pandas as pd

df = pd.read_csv('./drug_to_person.csv')
title = df['drug_to_person'].values

with open('./drug_to_person.txt', 'a') as f:
    for t in title[0:]:
        f.write(t + ' ' + 'nr' + '\n')
