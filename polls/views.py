from django.shortcuts import render
from django.conf import settings
# Create your views here.
from django.http import HttpResponse
import json
from plotly.offline import plot
import plotly.graph_objects as go



def index(request):

    return render(request, "welcome.html")

def environmental(request):

    return render(request, "environmental.html")



def tables(request):

    return render(request, "tables.html")


def radiation(request):

    return render(request, "radiation.html")


def comparison_rad(request):

    return render(request, "comparison_rad.html")

def comparison_temp(request):

    return render(request, "comparison_temp.html")


def comparison_co2(request):

    return render(request, "comparison_co2.html")


def comparison_rh(request):

    return render(request, "comparison_rh.html")
