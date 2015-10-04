from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import logout as auth_logout


def index(request):
    return render(request, 'home.html')


def logout(request):
    auth_logout(request)
    return redirect('newapp.views.index')


def register_after(request):
    return render(request, 'registration/register_after.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('newapp.views.register_after')
    else:
        form = CustomUserCreationForm()

    context = {
        'form': form,
    }
    return render(request, 'registration/register.html', context=context)
