from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import ItemForm, UserForm
from .models import Item


IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


def index(request):
    items = Item.objects.all()
    if not request.user.is_authenticated:
        return render(request, 'listing/index_visitor.html', {'items': items})
    else:
        # if a search is applied
        query = request.GET.get("q")
        if query:
            items = items.filter(
                Q(city__iexact=query)
            ).distinct()

        return render(request, 'listing/index.html', {'items': items})


def index_visitor(request):
    items = Item.objects.all()
    return render(request, 'listing/index_visitor.html', {'items': items})


def detail(request, item_id):
    if not request.user.is_authenticated:
        return render(request, 'listing/login.html')
    else:
        # user = request.user
        item = get_object_or_404(Item, pk=item_id)
        return render(request, 'listing/detail.html', {'item': item})


def add_item(request):
    if not request.user.is_authenticated:
        return render(request, 'listing/login.html')
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
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                }
                return render(request, 'listing/add_item.html', context)
            item.save()
            return render(request, 'listing/detail.html', {'item': item})
        context = {
            "form": form,
        }
        return render(request, 'listing/add_item.html', context)


def my_items(request):
    if not request.user.is_authenticated:
        return render(request, 'listing/login.html')
    else:
        items = Item.objects.filter(user=request.user)
        return render(request, 'listing/my_items.html', {'items': items})


def update_item(request, item_id):
    if not request.user.is_authenticated:
        return render(request, 'listing/login.html')
    else:
        item = Item.objects.get(pk=item_id)
        if item.user == request.user:
            form = ItemForm(request.POST or None, request.FILES or None, instance=item)
            if form.is_valid():
                file_type = item.photo.url.split('.')[-1]
                file_type = file_type.lower()
                if file_type not in IMAGE_FILE_TYPES:
                    context = {
                        'form': form,
                        'error_message': 'Image file must be PNG, JPG, or JPEG',
                    }
                    return render(request, 'listing/update_item.html', context)
                item.save()
                return render(request, 'listing/detail.html', {'item': item})
            context = {
                "form": form,
            }
            return render(request, 'listing/update_item.html', context)
        return render(request, 'listing/detail.html', {'item': item})


def delete_item(request, item_id):
    if not request.user.is_authenticated:
        return render(request, 'listing/login.html')
    else:
        item = Item.objects.get(pk=item_id)
        if item.user == request.user:
            item.delete()
        items = Item.objects.filter(user=request.user)
        return render(request, 'listing/my_items.html', {'items': items})


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                items = Item.objects.all()
                return render(request, 'listing/index.html', {'items': items})
    context = {
        "form": form,
    }
    return render(request, 'listing/register.html', context)


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'listing/login.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                items = Item.objects.all()
                return render(request, 'listing/index.html', {'items': items})
            else:
                return render(request, 'listing/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'listing/login.html', {'error_message': 'Invalid login'})
    return render(request, 'listing/login.html')




