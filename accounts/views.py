#from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect

def signup_disabled(request):
    return redirect("account_login")