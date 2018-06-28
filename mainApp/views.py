from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .forms import ItemForm, RegistrationForm
from .models import Item
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.images import get_image_dimensions
from django.conf import settings
import os


IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


def maintenance(request):
    return render(request, 'mainApp/maintenance.html')


def index(request):
    all_items = Item.objects.all().order_by('-id')
    page = request.GET.get('page', 1)
    paginator = Paginator(all_items, 18)
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)

    if not request.user.is_authenticated:
        return render(request, 'mainApp/index_visitor.html', {'items': items})
    else:
        user = request.user
        # if a search is applied
        query = request.GET.get("q")
        if query:
            found_items = all_items.filter(
                Q(city__iexact=query)
            ).distinct()
            page = request.GET.get('page', 1)
            paginator = Paginator(found_items, 18)
            try:
                items = paginator.page(page)
            except PageNotAnInteger:
                items = paginator.page(1)
            except EmptyPage:
                items = paginator.page(paginator.num_pages)

        return render(request, 'mainApp/index.html', {'items': items, 'user': user})


def detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if not request.user.is_authenticated:
        return render(request, 'mainApp/detail_visitor.html', {'item': item})
    else:
        return render(request, 'mainApp/detail.html', {'item': item})


def add_item(request):
    if not request.user.is_authenticated:
        return redirect('mainApp:login_user')
    else:
        form = ItemForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.photo = request.FILES['photo']
            file_type = item.photo.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'form': form,
                    'error_message': 'Image file type must be PNG, JPG or JPEG',
                }
                return render(request, 'mainApp/add_item.html', context)
            item.photo_width, item.photo_height = get_image_dimensions(item.photo)
            item.compress_image_save()
            return render(request, 'mainApp/detail.html', {'item': item})
        context = {
            "form": form,
        }
        return render(request, 'mainApp/add_item.html', context)


def my_items(request):
    if not request.user.is_authenticated:
        return redirect('mainApp:login_user')
    else:
        items = Item.objects.filter(user=request.user)
        return render(request, 'mainApp/my_items.html', {'items': items})


def terms(request):
    if request.user.is_authenticated:
        base_template_name = 'mainApp/base.html'
    else:
        base_template_name = 'mainApp/base_visitor.html'
    return render(request, 'mainApp/terms.html', {'base_template_name': base_template_name})


def about(request):
    if request.user.is_authenticated:
        base_template_name = 'mainApp/base.html'
    else:
        base_template_name = 'mainApp/base_visitor.html'
    return render(request, 'mainApp/about.html', {'base_template_name': base_template_name})


def update_item(request, item_id):
    if not request.user.is_authenticated:
        return redirect('mainApp:login_user')
    else:
        item = Item.objects.get(pk=item_id)
        photo_old = item.photo
        if item.user == request.user:
            form = ItemForm(request.POST or None, request.FILES or None, instance=item)
            if form.is_valid():
                file_type = item.photo.url.split('.')[-1]
                file_type = file_type.lower()
                if file_type not in IMAGE_FILE_TYPES:
                    context = {
                        'form': form,
                        'error_message': 'Image file type must be PNG, JPG or JPEG',
                    }
                    return render(request, 'mainApp/update_item.html', context)
                item.photo_width, item.photo_height = get_image_dimensions(item.photo)
                item.compress_image_save()

                # remove the old photo file
                image_path = settings.MEDIA_ROOT + '/' + photo_old.name
                if os.path.isfile(image_path):
                    os.remove(image_path)

                return render(request, 'mainApp/detail.html', {'item': item})
            context = {
                "form": form,
            }
            return render(request, 'mainApp/update_item.html', context)
        return render(request, 'mainApp/detail.html', {'item': item})


def delete_item(request, item_id):
    if not request.user.is_authenticated:
        return redirect('mainApp:login_user')
    else:
        item = Item.objects.get(pk=item_id)
        if item.user == request.user:
            item.delete()
        items = Item.objects.filter(user=request.user)
        return render(request, 'mainApp/my_items.html', {'items': items})


def register(request):
    if request.user.is_authenticated:
        return redirect('mainApp:index')
    else:
        form = RegistrationForm(request.POST or None)
        if request.recaptcha_is_valid:
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']
                form.save()
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('mainApp:index')
            else:
                context = {
                    "form": form,
                }
                return render(request, 'mainApp/register.html', context)
        else:
            if form.is_valid():
                context = {
                    "form": form,
                    "error_message": 'Please verify that you are not a robot.',
                }
            else:
                context = {
                    "form": form,
                }
            return render(request, 'mainApp/register.html', context)


def my_info(request):
    if not request.user.is_authenticated:
        return redirect('mainApp:login_user')
    else:
        user = request.user
        form = RegistrationForm(request.POST or None, instance=user)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            form.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('mainApp:index')
        context = {
            "form": form,
        }
        return render(request, 'mainApp/my_info.html', context)


def logout_user(request):
    logout(request)
    return redirect('mainApp:index')


def login_user(request):
    if request.user.is_authenticated:
        return redirect('mainApp:index')
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('mainApp:index')
                else:
                    return render(request, 'mainApp/login.html', {'error_message': 'Your account has been disabled.'})
            else:
                return render(request, 'mainApp/login.html', {'error_message': 'Invalid login! Please contact us for help if you forget your password.'})
        return render(request, 'mainApp/login.html')




