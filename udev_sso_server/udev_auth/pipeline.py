from .models import client_user
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.cache import cache
import uuid



def test(backend, uid, user=None, social=None, *args, **kwargs):
    if backend.name == 'weibo':
        weibo_user = client_user.objects.filter(weibo=uid)

        if weibo_user and len(weibo_user) > 0:
            #获取uid对应的用户
            username = weibo_user[0].user
            try:
                cas_user = User.objects.get(Q(username=username))
                cas_user.backend = 'django.contrib.auth.backends.ModelBackend'
            except Exception as e:
                return None
            if cas_user:
                session_id = uuid.uuid1()
                cache.set(session_id, cas_user, 60)
                redirect = HttpResponseRedirect('/to_login')
                redirect.set_cookie('uuid', session_id, 60)
                return redirect
        else:
            # 重定向到绑定页面
            session_id = uuid.uuid1()
            cache.set(session_id, {'uid': uid, 'provider': backend.name}, 120)
            redirect = HttpResponseRedirect('/binding')
            redirect.set_cookie('id', session_id, 120)
            return redirect