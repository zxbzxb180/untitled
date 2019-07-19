"""udev_sso_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin

from django.urls import include
from django.conf.urls import url
from django.urls import path
from udev_auth import views as auth_views
#import mama_cas.urls
from mama_cas.views import *


urlpatterns = [
    #url(r'', include('mama_cas.urls')),
    url(r'^logout/?$', LogoutView.as_view(), name='cas_logout'),
    url(r'^validate/?$', ValidateView.as_view(), name='cas_validate'),
    url(r'^serviceValidate/?$', ServiceValidateView.as_view(), name='cas_service_validate'),
    url(r'^proxyValidate/?$', ProxyValidateView.as_view(), name='cas_proxy_validate'),
    url(r'^proxy/?$', ProxyView.as_view(), name='cas_proxy'),
    url(r'^p3/serviceValidate/?$', ServiceValidateView.as_view(), name='cas_p3_service_validate'),
    url(r'^p3/proxyValidate/?$', ProxyValidateView.as_view(), name='cas_p3_proxy_validate'),
    url(r'^warn/?$', WarnView.as_view(), name='cas_warn'),
    url(r'^samlValidate/?$', SamlValidateView.as_view(), name='cas_saml_validate'),

    path(r'token', auth_views.token, name='auth_token'),


    url(r'^main/?$', auth_views.main, name='main'),
    url(r'^login/?$', auth_views.Login_urun.as_view(), name='cas_login'),

    url(r'^register/?$', auth_views.register, name='register'),
    url(r'^save/?$', auth_views.save, name='save'),

    url(r'^relation/?$', auth_views.relation, name='relation'),
    url(r'^add/?$', auth_views.add, name='add'),
    url(r'^reduce/?$', auth_views.reduce, name='reduce'),
    url(r'^delete/?$', auth_views.delete, name='delete'),

]
