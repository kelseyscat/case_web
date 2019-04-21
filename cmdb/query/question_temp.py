# -*- coding: utf-8 -*-
# 1. 某人员在哪个案件
# 2. 某案件有哪些被告人
# 3. 人员A和人员B是不是同伙
# 4. 被告人A和人员B存不存在交易关系
# 5. 某人员贩卖了多少次毒品
# 6. 某人员是贩毒人员吗
# 7. 某人员的基本信息
# 8. 某人员所在的案件有哪些被告人
# 9. 卖n克毒品判多少年
from refo import finditer, Predicate, Star, Any, Disjunction
import re

# TODO SPARQL前缀和模板
#加u是为了unicode
SPARQL_PREXIX = u""" 
PREFIX : <http://www.kgdemo.com#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

SPARQL_SELECT_TEM = u"{prefix}\n" + \
             u"SELECT DISTINCT {select} WHERE {{\n" + \
             u"{expression}\n" + \
             u"}}\n"

SPARQL_COUNT_TEM = u"{prefix}\n" + \
             u"SELECT COUNT({select}) WHERE {{\n" + \
             u"{expression}\n" + \
             u"}}\n"

SPARQL_ASK_TEM = u"{prefix}\n" + \
             u"ASK {{\n" + \
             u"{expression}\n" + \
             u"}}\n"


class W(Predicate):
    def __init__(self, token=".*", pos=".*"):
        self.token = re.compile(token + "$")
        self.pos = re.compile(pos + "$")
        super(W, self).__init__(self.match)

    def match(self, word):
        m1 = self.token.match(word.token)
        m2 = self.pos.match(word.pos)
        return m1 and m2


class Rule(object):
    def __init__(self, condition_num, condition=None, action=None):
        assert condition and action
        self.condition = condition
        self.action = action
        self.condition_num = condition_num

    def apply(self, sentence):
        matches = []
        for m in finditer(self.condition, sentence):
            i, j = m.span()
            matches.extend(sentence[i:j])

        return self.action(matches), self.condition_num


class KeywordRule(object):
    def __init__(self, condition=None, action=None):
        assert condition and action
        self.condition = condition
        self.action = action

    def apply(self, sentence):
        matches = []
        for m in finditer(self.condition, sentence):
            i, j = m.span()
            matches.extend(sentence[i:j])
        if len(matches) == 0:
            return None
        else:
            return self.action()


class QuestionSet:
    def __init__(self):
        pass

    @staticmethod
    def has_case_question(word_objects):
        # 某人员在哪个案件
        # :param word_objects:
        # :return:
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = u"?s :personName '{person}'." \
                    u"?s :hasCase ?m." \
                    u"?m :caseName ?x".format(person=w.token.decode('utf-8'))

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_person_question(word_objects):
        # 某案件有哪些人员
        # :param word_objects:
        # :return:
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_case:
                e = u"?m :caseName '{case}'." \
                    u"?m :hasPerson ?a." \
                    u"?a :personName ?x.".format(case=w.token.decode('utf-8'))
                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_cooperation_question(word_objects):
        # 人员A和人员B是不是同伙
        # :param word_objects:
        # :return:
        select = u"?x"

        person1 = None
        person2 = None

        for w in word_objects:
            if w.pos == pos_person:
                if person1 is None:
                    person1 = w.token
                else:
                    person2 = w.token
        if person1 is not None and person2 is not None:
            e = u"?p1 :personName '{person1}'." \
                u"?p2 :personName '{person2}'." \
                u"?p1 :hasCase ?m." \
                u"?p2 :hasCase ?m." \
                u"?m :caseName ?x".format(person1=person1.decode('utf-8'), person2=person2.decode('utf-8'))

            sparql = SPARQL_ASK_TEM.format(prefix=SPARQL_PREXIX, expression=e)
            return sparql
        else:
            return None

    @staticmethod
    def has_trade_question(word_objects):
        # 被告人A和人员B存不存在交易关系
        # :param word_objects:
        # :return:
        select = u"?x"

        person1 = None
        person2 = None

        for w in word_objects:
            if w.pos == pos_person:
                if person1 is None:
                    person1 = w.token
                else:
                    person2 = w.token
        if person1 is not None and person2 is not None:
            e = u"?c :drugToPerson '{person2}'." \
                u"?c :hasSelledBy ?p." \
                u"?p :personName ?x."\
                u"FILTER (?x='{person1}')".format(person1=person1.decode('utf-8'), person2=person2.decode('utf-8'))

            sparql = SPARQL_ASK_TEM.format(prefix=SPARQL_PREXIX, expression=e)
            return sparql
        else:
            return None

    @staticmethod
    def has_count_question(word_objects):
        # 某人员贩卖了多少次毒品
        # :param word_objects:
        # :return:
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = u"?s :personName '{person}'." \
                    u"?s :hasSell ?x.".format(person=w.token.decode('utf-8'))

                sparql = SPARQL_COUNT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_sell_drug_question(word_objects):
        # 被告人A是贩毒人员吗
        # :param word_objects:
        # :return:

        person = None

        for w in word_objects:
            if w.pos == pos_person:
                if person is None:
                    person = w.token

        if person is not None:
            e = u"?c :personName '{person}'." \
                u"?c :hasSell ?x.".format(person=person.decode('utf-8'))

            sparql = SPARQL_ASK_TEM.format(prefix=SPARQL_PREXIX, expression=e)
            return sparql
        else:
            return None

    @staticmethod
    def information_question(word_objects):
        # 某人员的基本信息
        # :param word_objects:
        # :return:
        select = u"?x ?m ?a"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = u"?s :personName '{person}'." \
                    u"?s :personSex ?m." \
                    u"?s :personBirthPlace ?a." \
                    u"?s :personBirthDay ?x.".format(person=w.token.decode('utf-8'))

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_person_case_question(word_objects):
        # 某人员所在案件有哪些被告人
        # :param word_objects:
        # :return:
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_person:
                e = u"?s :personName '{person}'." \
                    u"?s :hasCase ?m." \
                    u"?m :hasPerson ?z." \
                    u"?z :personName ?x.".format(person=w.token.decode('utf-8'))

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                break
        return sparql

    @staticmethod
    def has_judge_question(word_objects):
        # 卖n克毒品判多少年
        # :param word_objects:
        # :return:
        select = u"?x"

        sparql = None
        for w in word_objects:
            if w.pos == pos_number:
                e = u"?p :sellSum ?n." \
                    u"?p :penalJudge ?x." \
                    u"?p :crimeName ?y." \
                    u"FILTER (?n>={number} && ?y=\"{nameSet}\")".format(number=w.token.decode('utf-8'),nameSet=define.decode('utf-8'))

                sparql = SPARQL_SELECT_TEM.format(prefix=SPARQL_PREXIX,
                                                  select=select,
                                                  expression=e)
                sparql+=u"ORDER BY (?n)\nLIMIT 1"
                break
        return sparql


# TODO 定义关键词
define="贩卖毒品罪"
pos_case= "nz"
pos_person = "nr"
pos_drug = "nz"
pos_drug_to_person="nr"
pos_number="m"

person_entity = (W(pos=pos_person))
case_entity = (W(pos=pos_case))
drug_entity = (W(pos=pos_drug))
drug_to_person_entity = (W(pos=pos_drug_to_person))

case = (W("案件") | W("案子") | W("参案"))
person = (W("人") | W("人员") | W("被告人"))
cooperation= (W("同伙") | W("同伴"))
trade = (W("交易关系")| W("交易"))
drug=(W("毒品"))
several = (W("多少") | W("几次"))
seller= (W("贩毒人员") )
information= (W("基本信息") | W("基本资料"))
sell=(W("贩卖") | W("卖"))
time=(W("年")| W("时间"))

rules = [
    Rule(condition_num=2, condition=person_entity + Star(Any(), greedy=False) + case + Star(Any(), greedy=False), action=QuestionSet.has_case_question),
    Rule(condition_num=2, condition=case_entity + Star(Any(), greedy=False) + person + Star(Any(), greedy=False), action=QuestionSet.has_person_question),
    Rule(condition_num=3, condition=person_entity + Star(Any(), greedy=False) + person_entity + Star(Any(), greedy=False) + cooperation, action=QuestionSet.has_cooperation_question),
    Rule(condition_num=3, condition=person_entity + Star(Any(), greedy=False) + drug_to_person_entity + Star(Any(), greedy=False) + trade, action=QuestionSet.has_trade_question),
    Rule(condition_num=3, condition=person_entity + Star(Any(), greedy=False) + several + Star(Any(), greedy=False) + drug, action=QuestionSet.has_count_question),
    Rule(condition_num=2, condition=person_entity + Star(Any(), greedy=False) + seller+  Star(Any(), greedy=False), action=QuestionSet.has_sell_drug_question),
    Rule(condition_num=2, condition=person_entity + Star(Any(), greedy=False) + information + Star(Any(), greedy=False), action=QuestionSet.information_question),
    Rule(condition_num=3, condition=person_entity + Star(Any(), greedy=False) + case + Star(Any(), greedy=False) + person, action=QuestionSet.has_person_case_question),
    Rule(condition_num=4, condition=sell + Star(Any(), greedy=False) + drug + Star(Any(), greedy=False) + several + time, action=QuestionSet.has_judge_question),
]
