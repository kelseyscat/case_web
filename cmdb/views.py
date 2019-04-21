# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from django.shortcuts import render
from django.shortcuts import HttpResponse
import query.query_main as q
# Create your views here.
from cmdb.query import jena_sparql_endpoint, question2sparql
test_list=[]
def index(request):
    # return HttpResponse("hello world!")
    # return render(request,"bg.html")
    if request.method=='POST':
        que=request.POST.get("searchResult",None)
        re=q.searchMain(que)
        temp ={"question":que,"answer":re}
        test_list.append(temp)
        print(re)
    return render(request,"bg.html",{"data":test_list})

def menu(request):
    # return HttpResponse("hello world!")
    return render(request,"menu.html")

def display(request):
    # return HttpResponse("hello world!")
    return render(request,"java.html")
