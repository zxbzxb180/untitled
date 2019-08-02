from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from django_cas_ng import views as cas_views
import client_app2.views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('login/', cas_views.LoginView.as_view(), name='cas_ng_login'),
    path('logout/', cas_views.LogoutView.as_view(), name='cas_ng_logout'),
    path('callback/', cas_views.CallbackView.as_view(), name='cas_ng_proxy_callback'),
    path('', client_app2.views.homepage),
]