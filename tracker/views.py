from inspect import getargs
from django.http import HttpResponse
from django.shortcuts import render
from tracker.middlewares import get_request

# Create your views here.

def testMiddleware(request):
    # print("testMiddleware")
    # print(get_request())
    # print(get_request() is None)
    # print(getattr(get_request(), "user", None))

    # print("test Getattr")
    # print(getattr(None, "user", "hi"))
    return HttpResponse(get_request().user.id)