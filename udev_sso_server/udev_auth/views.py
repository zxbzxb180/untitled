import hashlib
import json
import logging
import time
import traceback
from django.shortcuts import render
from django.http import HttpResponse
from udev_sso_server.settings import admin_account_list
from .models import *
from bson import ObjectId
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from login.user import user_db, cas_db
from .tokener import dumps as token_dumps
from django.contrib import messages
from django.core.cache import cache
from mama_cas.views import *
from mama_cas.models import *

import re


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('udev_auth')


def make_token(appid, timestamp, sign, expire=3600):
    if not appid or not timestamp or not sign:
        return dict(status=False, data='', code=400, msg='missing argument')

    current_time = int(time.time())
    if current_time - int(timestamp) > 300:
        return dict(status=False, data='', code=408, msg='sign expired')

    dev = cas_db.app_dev.find_one({'app_id': appid})
    if not dev:
        return dict(status=False, data='', code=404, msg='invalid appid')
    if not dev['app_secret']:
        return dict(status=False, data='', code=405, msg='the user is not a developer')

    appsecret = dev['app_secret']

    # node = db.node.find_one({'_id': ObjectId(appid)})
    # if not node:
    #    return dict(status=False, data='', code=404, msg='invalid appid')
    # user = db.user.find_one({'_id': ObjectId(node['value'])}) or {}
    # appsecret = user.get('app_secret', '')
    md5 = appid + appsecret + timestamp
    confirm = hashlib.md5(md5.encode('utf8')).hexdigest()

    if confirm != sign:
        log.debug('sign %s not match %s, appid: %s, appsecret: %s', confirm, sign, appid, appsecret)
        return dict(status=False, data='', code=500, msg='invalid sign')

    user = user_db.user.find_one({'_id': ObjectId(appid)})
    if not user:
        log.error('can not found developer user: %s', appid)
        return dict(status=False, data='', code=500, msg='can not found developer')

    token = token_dumps({
        'id': str(user['_id']),
        "name": user["name"],
        "alias": user["alias"]
    }, int(expire))

    return dict(status=True, data=token.decode('utf8'), code=0, msg='')


def with_json_response(func):
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        return JsonResponse(result)

    return inner


@csrf_exempt
@with_json_response
def token(request):
    data = request.body
    if isinstance(data, bytes):
        data = data.decode()

    try:
        data = json.loads(data)
    except Exception:
        traceback.print_exc()
        return dict(status=False, data="", code=2, msg="invalid json format.")

    if 'appsecret' in data:
        return dict(status=False, data="", code=3, msg="do not pass appsecret")

    if not data.get('expire'):
        data['expire'] = 3600

    try:
        return make_token(**data)
    except Exception as e:
        return dict(status=False, data="", code=1, msg=str(e))



class Login_urun(LoginView):

    def get_form_kwargs(self):
        kwargs = super(Login_urun, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        service = request.GET.get('service')
        renew = to_bool(request.GET.get('renew'))
        gateway = to_bool(request.GET.get('gateway'))


        if renew:
            logger.debug("Renew request received by credential requestor")
        elif gateway and service:
            logger.debug("Gateway request received by credential requestor")
            if is_authenticated(request.user):
                st = ServiceTicket.objects.create_ticket(service=service, user=request.user)
                if self.warn_user():
                    return redirect('cas_warn', params={'service': service, 'ticket': st.ticket})
                return redirect(service, params={'ticket': st.ticket})
            else:
                return redirect(service)

        #已通过身份验证
        elif is_authenticated(request.user):
            if service:
                try:
                    service = (re.findall(r"(.+?)\?next", service))[0]
                except IndexError:
                    pass
                logger.debug("Service ticket request received by credential requestor")
                user_id = client_user.objects.get(user=self.request.user)
                name = client_list.objects.get(url=service)
                if cas_client.objects.filter(name=name.name, user_id=user_id.id):
                    access = cas_client.objects.get(name=name.name, user_id=user_id.id)
                    if access.access == 1:
                        st = ServiceTicket.objects.create_ticket(service=service, user=request.user)
                        if self.warn_user():
                            return redirect('cas_warn', params={'service': service, 'ticket': st.ticket})
                        return redirect(service, params={'ticket': st.ticket})
                    else:
                        return HttpResponse('<h2 align="center">'+str(self.request.user) +'无权访问客户端</h2>')
                else:
                    return HttpResponse('<h2 align="center">'+str(self.request.user) +'无权访问客户端</h2>')
            else:
                msg = _("You are logged in as %s") % request.user
                messages.success(request, msg)
                return redirect('main')


        #未验证身份
        return super(Login_urun, self).get(request, *args, **kwargs)

    #账号密码有效
    def form_valid(self, form):

        if not client_user.objects.filter(user=form.user):
            client_user.objects.create(user=form.user)
        if 'id' in self.request.COOKIES:
            id = self.request.COOKIES['id']
            if cache.get(id)['provider'] == 'weibo':
                client_user.objects.filter(user=form.user).update(weibo=cache.get(id)['uid'])

        login(self.request, form.user)
        logger.info("Single sign-on session started for %s" % form.user)

        if form.cleaned_data.get('warn'):
            self.request.session['warn'] = True

        service = self.request.GET.get('service')

        if service:
            try:
                service = (re.findall(r"(.+?)\?next", service))[0]
            except IndexError:
                pass
            st_client = ServiceTicket.objects.create_ticket(service=service, user=self.request.user, primary=True)
            user_id = client_user.objects.get(user=self.request.user)
            name = client_list.objects.get(url=service)
            if cas_client.objects.filter(name=name.name, user_id=user_id.id):
                access = cas_client.objects.get(name=name.name, user_id=user_id.id)

                if access.access == 1:
                    return redirect(service, params={'ticket': st_client.ticket})

                else:
                    return HttpResponse('<h2 align="center">'+str(self.request.user) +'无权访问客户端</h2>')

            else:
                return HttpResponse('<h2 align="center">'+str(self.request.user) +'无权访问客户端</h2>')




        else:
            return redirect('main')

class Logout_urun(LogoutView):

    def get(self, request, *args, **kwargs):

        service = request.GET.get('service')

        if not service:
            service = request.GET.get('url')


        follow_url = getattr(settings, 'MAMA_CAS_FOLLOW_LOGOUT_URL', True)

        logout_user(request)

        if service and follow_url:
            return redirect(service)
        return redirect('cas_login')



def main(request):
    if is_authenticated(request.user):
        results = client_list.objects.all()

        return render(request, 'main.html', {'results': results,
                                             'admin_account_list': admin_account_list})
    else:
        return redirect('cas_login')

def manage(request):
    if request.user.username in admin_account_list:
        results = client_list.objects.all()
        return render(request, 'manage.html', {'results': results})


def alter_client(request):
    if request.user.username in admin_account_list:
        name = request.GET.get('name')
        result = client_list.objects.get(name=name)
        return render(request, 'alter.html', {'name': name,
                                          'result': result})


def alter(request):
    if request.user.username in admin_account_list:
        name = request.GET.get('name')
        if not (client_list.objects.filter(name=request.POST['name']) or client_list.objects.filter(url=request.POST['url']) or client_list.objects.filter(callback=request.POST['callback'])):
            service = client_list.objects.get(name=name)
            ServiceTicket.objects.filter(service=service.url).update(service=request.POST['url'])
            cas_client.objects.filter(name=name).update(name=request.POST['name'])
            if request.POST['img']:
                client_list.objects.filter(name=name).update(name=request.POST['name'], url=request.POST['url'], callback=request.POST['callback'], img=request.FILES.get('img'))
            else:
                client_list.objects.filter(name=name).update(name=request.POST['name'], url=request.POST['url'], callback=request.POST['callback'])
        else:
            return HttpResponse('<h2 align="center">该名称或url或回调地址已存在</h2>')

        return HttpResponse('<h2 align="center">修改成功</h2>')


def delete(request):
    if request.user.username in admin_account_list:
        name = request.GET.get('name')
        client_list.objects.filter(name=name).delete()
        cas_client.objects.filter(name=name).delete()
        return redirect('manage')


def register(request):
    if request.user.username in admin_account_list:
        return render(request, 'register.html')


def save(request):
    if request.user.username in admin_account_list:
        if not (client_list.objects.filter(name=request.POST['name']) or client_list.objects.filter(url=request.POST['url']) or client_list.objects.filter(callback=request.POST['callback'])):
            client_list.objects.create(name=request.POST['name'], url=request.POST['url'], img=request.FILES.get('img'), callback=request.POST['callback'])
        else:
            return HttpResponse('<h2 align="center">该名称或url或回调地址已存在</h2>')
        return HttpResponse('<h2 align="center">注册成功</h2>')


def relation(request):
    if request.user.username in admin_account_list:
        return render(request, 'relation.html')


def add(request):
    if request.user.username in admin_account_list:
        if client_user.objects.filter(user=request.POST['user']) and client_list.objects.filter(name=request.POST['name']):
            user_id = client_user.objects.get(user=request.POST['user'])
            if not cas_client.objects.filter(name=request.POST['name'], user_id=user_id.id):
                cas_client.objects.create(name=request.POST['name'], access=1, user_id=user_id.id)
            return redirect('relation')
        else:
            return HttpResponse('<h2 align="center">用户或客户端不存在</h2>')


def reduce(request):
    if request.user.username in admin_account_list:
       if client_user.objects.filter(user=request.POST['user']) and client_list.objects.filter(name=request.POST['name']):
            user_id = client_user.objects.get(user=request.POST['user'])
            cas_client.objects.filter(name=request.POST['name'], user_id=user_id.id).delete()
            return redirect('relation')
       else:
           return HttpResponse('<h2 align="center">用户或客户端不存在</h2>')

def to_login(request):
    if 'uuid' in request.COOKIES:
        uuid = request.COOKIES['uuid']
        user = cache.get(uuid)
        login(request, user)
        return redirect('main')



class binding(Login_urun):
    template_name = 'binding.html'

