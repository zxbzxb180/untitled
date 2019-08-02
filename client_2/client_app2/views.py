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




