from urllib.request import urlopen
import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from xml.etree import ElementTree
import pymysql


# cas服务器地址
CAS_host = 'http://127.0.0.1:30000/'

def login(request):
    # if request.COOKIES.get('username'):
    #     return HttpResponse('已登录')

    #获取ticket
    tkt = request.GET.get('ticket')

    # 没有ticket，重定向到cas服务端登录页面
    if not tkt:
        #重定向url
        redirect = CAS_host + 'login?service=' + request.build_absolute_uri()

        return HttpResponseRedirect(redirect)





    #验证ticket是否有效
    check = CAS_host + 'serviceValidate?ticket=' + tkt + '&service=' + request.build_absolute_uri('?')

    #打开页面
    response = requests.get(check)


    userid = ''

    #若响应为空，则验证信息为空
    if response.text == '':
        return HttpResponse('验证信息为空')

    #响应不为空，判断验证是否通过
    else:
        # 验证未通过
        if 'not recognized' in response.text:
            return HttpResponse("ticket验证失败")

        #验证通过，获取用户
        else:
            tree = ElementTree.fromstring(response.text)

            if 'INVALID_TICKET' in response.text:

                return HttpResponse('ticket已失效')

            elif 'INVALID_SERVICE' in response.text:
                return HttpResponse('service无效')



            userid = tree[0][0].text



            #设置session保持登录
            #request.session['username'] = userid


            return HttpResponseRedirect('http://127.0.0.1:8000/')




