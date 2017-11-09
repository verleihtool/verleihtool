from django.shortcuts import render


def home(request):
    return render(request, 'login/home.html', {
        'logged_in': request.user.is_authenticated,
        'superuser': request.user.is_superuser
    })
