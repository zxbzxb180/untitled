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
from django.conf.urls.static import static
from mama_cas.views import *
from django.contrib import admin
import oauth2_provider.views as oauth2_views
from django.conf import settings
from udev_oauth2.views import *




oauth2_endpoint_views = [
    url(r'^authorize/$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', oauth2_views.TokenView.as_view(), name="token"),
    url(r'^revoke-token/$', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

if settings.DEBUG:
    # OAuth2 Application Management endpoints
    oauth2_endpoint_views += [
        url(r'^applications/$', oauth2_views.ApplicationList.as_view(), name="list"),
        url(r'^applications/register/$', oauth2_views.ApplicationRegistration.as_view(), name="register"),
        url(r'^applications/(?P<pk>\d+)/$', oauth2_views.ApplicationDetail.as_view(), name="detail"),
        url(r'^applications/(?P<pk>\d+)/delete/$', oauth2_views.ApplicationDelete.as_view(), name="delete"),
        url(r'^applications/(?P<pk>\d+)/update/$', oauth2_views.ApplicationUpdate.as_view(), name="update"),
    ]

    # OAuth2 Token Management endpoints
    oauth2_endpoint_views += [
        url(r'^authorized-tokens/$', oauth2_views.AuthorizedTokensListView.as_view(), name="authorized-token-list"),
        url(r'^authorized-tokens/(?P<pk>\d+)/delete/$', oauth2_views.AuthorizedTokenDeleteView.as_view(),
            name="authorized-token-delete"),
    ]


urlpatterns = [
    url(r'^logout/?$', auth_views.Logout_urun.as_view(), name='cas_logout'),
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

    url(r'^manage/?$', auth_views.manage, name='manage'),
    url(r'^alter_client/?$', auth_views.alter_client, name='alter_client'),
    url(r'^alter/?$', auth_views.alter, name='alter'),
    url(r'^delete/?$', auth_views.delete, name='delete'),


    # 第三方登录(作为客户端)
    url('', include('social_django.urls')),
    path('to_login/', auth_views.to_login),
    path('binding/', auth_views.binding.as_view(), name='binding'),


    #第三方认证(作为服务端)
    url(r"^admin/", admin.site.urls),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('accounts/', include('django.contrib.auth.urls')),
    url(r'^api/hello', ApiEndpoint.as_view()),  # an example resource endpoint
    url(r'^secret$', secret_page, name='secret'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# OAuth2 provider endpoints
oauth2_endpoint_views = [
    url(r'^authorize/$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', oauth2_views.TokenView.as_view(), name="token"),
    url(r'^revoke-token/$', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

if settings.DEBUG:
    # OAuth2 Application Management endpoints
    oauth2_endpoint_views += [
        url(r'^applications/$', oauth2_views.ApplicationList.as_view(), name="list"),
        url(r'^applications/register/$', oauth2_views.ApplicationRegistration.as_view(), name="register"),
        url(r'^applications/(?P<pk>\d+)/$', oauth2_views.ApplicationDetail.as_view(), name="detail"),
        url(r'^applications/(?P<pk>\d+)/delete/$', oauth2_views.ApplicationDelete.as_view(), name="delete"),
        url(r'^applications/(?P<pk>\d+)/update/$', oauth2_views.ApplicationUpdate.as_view(), name="update"),
    ]

    # OAuth2 Token Management endpoints
    oauth2_endpoint_views += [
        url(r'^authorized-tokens/$', oauth2_views.AuthorizedTokensListView.as_view(), name="authorized-token-list"),
        url(r'^authorized-tokens/(?P<pk>\d+)/delete/$', oauth2_views.AuthorizedTokenDeleteView.as_view(),
            name="authorized-token-delete"),
    ]