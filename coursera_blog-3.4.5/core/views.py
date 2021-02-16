from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'core/index.html')


def index2(request):
    return render(request, 'core/index2.html')


def topic_details(request, pk):
    return render(request, 'core/topic_details.html')
