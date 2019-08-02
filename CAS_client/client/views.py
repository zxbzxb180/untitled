from urllib.request import urlopen
import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from xml.etree import ElementTree
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.conf import settings
from importlib import import_module


SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

# cas服务器地址
CAS_host = 'http://127.0.0.1:30000/'

def login(request):
    if request.method == 'GET':
        if request.COOKIES.get('sessionid_client_1_cas'):
            return HttpResponse('已登录')

        #获取ticket
        tkt = request.GET.get('ticket')
        service_url = request.build_absolute_uri()
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


                if 'INVALID_TICKET' in response.text:

                    return HttpResponse('ticket已失效')

                elif 'INVALID_SERVICE' in response.text:
                    return HttpResponse('service无效')


                #获取用户名
                tree = ElementTree.fromstring(response.text)
                userid = tree[0][0].text
                print(userid)





                #v = HttpResponseRedirect('http://127.0.0.1:8000/')
                v = HttpResponse('登录成功！')
                auth_login(request, request.user)
                request.session.create()
                return v

    elif request.method == 'POST':
        if request.POST.get('logoutRequest'):
            print(request.POST.get('logoutRequest'))
        print('退出')
        session = SessionStore(session_key=request.COOKIES.get('sessionid_client_1_cas'))
        session.flush()
        return HttpResponse('退出')


def logout(request):
    if request.POST.get('logoutRequest'):
        print(request.POST.get('logoutRequest'))
    print('退出')
    #session = SessionStore(session_key=request.COOKIES.get('sessionid_client_1_cas'))
    request.session.flush()
    return HttpResponse('退出')


