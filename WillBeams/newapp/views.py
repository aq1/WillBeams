from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
# from .forms import CustomUserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout as auth_logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

from .models import Webm, UserLike, UserFavourite, UserNsfw


def logout(request):
    auth_logout(request)
    return redirect('home')


def register_after(request):
    return render(request, 'registration/register_after.html', context={'active': 'register'})


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
        'active': 'register',
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
        'webm_count': items.count(),
        'label': label,
        'active': active,
    }
    context.update(kwargs)
    return render(request, 'video/list.html', context=context)


def new_videos(request):
    return abstract_videos(
        request,
        Webm.objects.all().order_by('-added', '-id'),  # stable ordering
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


@ensure_csrf_cookie
def video(request, vid):
    webm = get_object_or_404(Webm, pk=vid)
    next_webm = Webm.objects.filter(added__lte=webm.added, id__lt=webm.pk)\
        .order_by('-added', '-id').first()
    prev_webm = Webm.objects.filter(added__gte=webm.added, id__gt=webm.pk)\
        .order_by('added', 'id').first()
    data = {
        'webm': webm,
        'next': next_webm,
        'prev': prev_webm,
    }
    if request.user.is_authenticated():
        data['video_like'] = webm.userlike.filter(user=request.user).exists()
        data['video_favourite'] = webm.userfavourite.filter(user=request.user).exists()
        data['video_nsfw'] = webm.usernsfw.filter(user=request.user).exists()
    return render(request, 'video/view.html', context=data)


def _toggler(request, model):
    if request.method != 'POST':
        return HttpResponse('Bad method, must be POST', status=400)
    webm = get_object_or_404(Webm, pk=request.POST.get('id'))
    state = request.POST.get('state')
    if state not in ('true', 'false'):
        return HttpResponse('Bad state value, must be true or false', status=400)
    state = state == 'true'

    try:
        mrec = model.objects.get(user=request.user, webm=webm)
        if not state:
            mrec.delete()
    except model.DoesNotExist:
        if state:
            mrec = model(user=request.user, webm=webm)
            mrec.save()

    return HttpResponse('true' if state else 'false', status=200, content_type='application/json')


@login_required
def toggle_like(request):
    return _toggler(request, UserLike)


@login_required
def toggle_favourite(request):
    return _toggler(request, UserFavourite)


@login_required
def toggle_nsfw(request):
    return _toggler(request, UserNsfw)
