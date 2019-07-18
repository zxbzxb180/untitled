import hashlib
import json
import logging
import time
import traceback
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect

from bson import ObjectId
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from login.user import user_db, cas_db
from .tokener import dumps as token_dumps

from mama_cas.views import *
import requests

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

        # self.request.GET.get('service')
        #print(self.request.GET.get('ticket'))
        # if 'username' in self.request.session and service == None:
        #     print(self.request.session['username'])
        #     ticket_r = request.GET.get('ticket')
        #     return redirect('main', params={'ticket': ticket_r})



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

        elif is_authenticated(request.user):
            print(request.user)
            if service:
                logger.debug("Service ticket request received by credential requestor")
                st = ServiceTicket.objects.create_ticket(service=service, user=request.user)
                if self.warn_user():
                    return redirect('cas_warn', params={'service': service, 'ticket': st.ticket})
                return redirect(service, params={'ticket': st.ticket})
            else:

                #msg = _("You are logged in as %s") % request.user
                msg = ("You are logged in as %s") % request.user
                messages.success(request, msg)

                return redirect('main')

        return super(Login_urun, self).get(request, *args, **kwargs)

    def form_valid(self, form):

        login(self.request, form.user)
        logger.info("Single sign-on session started for %s" % form.user)

        if form.cleaned_data.get('warn'):
            self.request.session['warn'] = True

        service = self.request.GET.get('service')
        # st = ServiceTicket.objects.create_ticket(user=self.request.user, primary=True)

        if service:
            st_client = ServiceTicket.objects.create_ticket(service=service, user=self.request.user, primary=True)
            return redirect(service, params={'ticket': st_client.ticket})


        else:
            #self.request.session['username'] = self.request.POST['username']

            #st = ServiceTicket.objects.create_ticket(user=self.request.user, primary=True)
            #return redirect('main', params={'ticket': st.ticket})
            #self.request.session['tkt'] = st
            return redirect('main')





def main(request):
    if is_authenticated(request.user):
        return render(request, 'main.html')
    # if 'username' not in request.session:
    #     print('没有username')
    else:
        return redirect('cas_login')
    # user = request.session['username']
    # print(user)
    #
    # if 'tkt' not in request.session:
    #     return render(request, 'main.html')
    # tkt = request.session['tkt']
    # print(tkt)

    #return render(request, 'main.html', {'ticket': tkt})

    #print(request.session)


