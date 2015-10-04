from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm


def index(request):
    return render(request, 'home.html')


def register_after(request):
    return render(request, 'registration/register_after.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('newapp.views.register_after')
    else:
        form = UserCreationForm()

    context = {
        'form': form,
    }
    return render(request, 'registration/register.html', context=context)
