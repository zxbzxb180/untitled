from django.shortcuts import render
from django.http import HttpResponse
from client_2.settings import CAS_SERVER_URL
import requests
from xml.etree import ElementTree
from django_cas_ng.views import *
from django.http import HttpResponseRedirect



def homepage(request):
    if request.user.is_authenticated:
        return HttpResponse("Hello {}. <a href='/logout'>Logout</a>".format(request.user.username))
    else:
        return HttpResponse("Not logged in. <a href='/login'>Login</a>")


class LoginView_2(LoginView):
    def successful_login(self, request, next_page):
        """
        This method is called on successful login. Override this method for
        custom post-auth actions (i.e, to add a cookie with a token).

        :param request:
        :param next_page:
        :return:
        """
        return HttpResponseRedirect('http://127.0.0.1:8001/')

