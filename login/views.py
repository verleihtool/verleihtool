from django.shortcuts import render

# Create your views here.

from django.contrib.auth import authenticate, login, logout


def home(request):
	return render(request, 'login/home.html', {'logged_in': request.user.is_authenticated})
