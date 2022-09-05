from django.http import HttpResponse
from django.shortcuts import render
from tracker.middlewares import get_request

# Create your views here.

def testMiddleware(request):
    return HttpResponse(get_request().user.id)