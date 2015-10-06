from django.shortcuts import render, redirect
# from .forms import CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout as auth_logout

from .models import Webm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index(request):
    return render(request, 'home.html')


def logout(request):
    auth_logout(request)
    return redirect('newapp.views.index')


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

# Video views


def new_videos(request):
    paginator = Paginator(
        Webm.objects.all().order_by('-added'),
        20
    )
    try:
        webm_list = paginator.page(request.GET.get('page'))
    except PageNotAnInteger:
        webm_list = paginator.page(1)
    except EmptyPage:
        webm_list = paginator.page(paginator.num_pages)
    return render(request, 'video/list.html', context={
        'webm_list': webm_list
    })
