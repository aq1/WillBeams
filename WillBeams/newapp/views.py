from django.shortcuts import render, redirect, get_object_or_404
# from .forms import CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout as auth_logout

from .models import Webm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required


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


def abstract_videos(request, items, label, active, **kwargs):
    paginator = Paginator(
        items,
        20
    )
    try:
        webm_list = paginator.page(request.GET.get('page'))
    except PageNotAnInteger:
        webm_list = paginator.page(1)
    except EmptyPage:
        webm_list = paginator.page(paginator.num_pages)
    context = {
        'webm_list': webm_list,
        'label': label,
        'active': active,
    }
    context.update(kwargs)
    return render(request, 'video/list.html', context=context)


def new_videos(request):
    return abstract_videos(
        request,
        Webm.objects.all().order_by('-added'),
        'Новые',
        'new',
    )


@login_required
def liked_videos(request):
    return abstract_videos(
        request,
        Webm.objects.filter(likes=request.user).order_by('-userlike__time'),
        'Понравившиеся',
        'liked',
    )


@login_required
def favourite_videos(request):
    return abstract_videos(
        request,
        Webm.objects.filter(favourite=request.user).order_by('-userfavourite__time'),
        'Избранные',
        'favourite',
    )


def tag_videos(request, tag):
    return abstract_videos(
        request,
        Webm.objects.filter(tag__name=tag).order_by('-added'),
        'Тег ' + tag,
        'tag',
        tag=tag
    )


def video(request, vid):
    webm = get_object_or_404(Webm, pk=vid)
    return render(request, 'video/view.html', context={'webm': webm})
