from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .forms import ItemForm, RegistrationForm, ProfileForm, ItemFormForAdd
from .models import Item, Ad, Profile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.images import get_image_dimensions
from django.conf import settings
import os


IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


def maintenance(request):
    return render(request, 'mainApp/maintenance.html')


def donate(request):
    if request.user.is_authenticated:
        base_template_name = 'mainApp/base.html'
    else:
        base_template_name = 'mainApp/base_visitor.html'
    return render(request, 'mainApp/donate.html', {'base_template_name': base_template_name})


def index(request):
    all_items = Item.objects.all().order_by('-id')
    all_ads = Ad.objects.all()

    # if a search is applied
    query = request.GET.get("q")
    if query:
        found_ads = all_ads.filter(
            Q(city__iexact=query)
        ).distinct()
        if found_ads.count():
            ad = found_ads[0]
        else:
            ad = 0
        found_items = all_items.filter(
            Q(city__icontains=query)
        ).distinct()
        page = request.GET.get('page', 1)
        paginator = Paginator(found_items, 36)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
    else:
        found_ads = all_ads.filter(
            Q(city__iexact='global')
        ).distinct()
        if found_ads.count():
            ad = found_ads[0]
        else:
            ad = 0
        page = request.GET.get('page', 1)
        paginator = Paginator(all_items, 36)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)

    if not request.user.is_authenticated:
        return render(request, 'mainApp/index_visitor.html', {'items': items, 'ad': ad})
    else:
        user = request.user
        return render(request, 'mainApp/index.html', {'items': items, 'ad': ad, 'user': user})


def detail(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    if not request.user.is_authenticated:
        return render(request, 'mainApp/detail_visitor.html', {'item': item})
    else:
        return render(request, 'mainApp/detail.html', {'item': item})


def add_item(request):
    all_profiles = Profile.objects.all()

    if not request.user.is_authenticated:
        return redirect('mainApp:login_user')
    else:
        # search for user's profile
        found_profile = all_profiles.filter(
            Q(user__exact=request.user)
        ).distinct()

        form = ItemFormForAdd(request.POST or None, request.FILES or None)
        # check if user's profile already exists, if yea, load the instance
        if found_profile.count():
            profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=found_profile[0])
        else:
            profile_form = ProfileForm(request.POST or None, request.FILES or None)

        if form.is_valid() and profile_form.is_valid():
            # create an item instance
            item = form.save(commit=False)

            item.user = request.user
            # check if user's profile already exists, if not, create a profile instance
            if found_profile.count():
                profile = found_profile[0]
            else:
                profile = profile_form.save(commit=False)

                profile.user = request.user
            # get item city and contact info from the profile form
            item.city = profile_form.cleaned_data['city']
            item.contact_info = profile_form.cleaned_data['contact_info']

            # check if the file types of the uploaded images are okay
            item.photo = request.FILES['photo']

            file_type = item.photo.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'form': form,
                    'profile_form': profile_form,
                    'error_message': 'Image file type must be PNG, JPG or JPEG',
                }
                return render(request, 'mainApp/add_item.html', context)

            # try except - error handling (request.FILES has MultiValueDictKeyError if another_photo is not filled)
            try:
                item.another_photo = request.FILES['another_photo']

                file_type = item.another_photo.url.split('.')[-1]
                file_type = file_type.lower()
                if file_type not in IMAGE_FILE_TYPES:
                    context = {
                        'form': form,
                        'profile_form': profile_form,
                        'error_message': 'Image file type must be PNG, JPG or JPEG',
                    }
                    return render(request, 'mainApp/add_item.html', context)

            except (KeyError):
                pass

            # try except - error handling (request.FILES has MultiValueDictKeyError if and_another_photo is not filled)
            try:
                item.and_another_photo = request.FILES['and_another_photo']

                file_type = item.and_another_photo.url.split('.')[-1]
                file_type = file_type.lower()
                if file_type not in IMAGE_FILE_TYPES:
                    context = {
                        'form': form,
                        'profile_form': profile_form,
                        'error_message': 'Image file type must be PNG, JPG or JPEG',
                    }
                    return render(request, 'mainApp/add_item.html', context)

            except (KeyError):
                pass

            item.photo_width, item.photo_height = get_image_dimensions(item.photo)
            item.compress_image_save()
            # save/update profile instance
            profile_form.save(commit=True)

            return render(request, 'mainApp/detail.html', {'item': item})
        # if any form is not valid.
        context = {
            'form': form,
            'profile_form': profile_form
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
        base_template_name = 'mainApp/base_visitor_kate.html'
    return render(request, 'mainApp/terms.html', {'base_template_name': base_template_name})


def about(request):
    if request.user.is_authenticated:
        base_template_name = 'mainApp/base.html'
    else:
        base_template_name = 'mainApp/base_visitor_kate.html'
    return render(request, 'mainApp/about.html', {'base_template_name': base_template_name})


def update_item(request, item_id):
    if not request.user.is_authenticated:
        return redirect('mainApp:login_user')
    else:
        item = Item.objects.get(pk=item_id)
        photo_old = item.photo
        another_photo_old = item.another_photo
        and_another_photo_old = item.and_another_photo
        if item.user == request.user:
            form = ItemForm(request.POST or None, request.FILES or None, instance=item)
            if form.is_valid():

                # check weather the file types of the image files are okay
                file_type = item.photo.url.split('.')[-1]
                file_type = file_type.lower()
                if file_type not in IMAGE_FILE_TYPES:
                    context = {
                        'form': form,
                        'error_message': 'Image file type must be PNG, JPG or JPEG',
                    }
                    return render(request, 'mainApp/update_item.html', context)

                # try except - error handling (request.FILES has ValueError if another_photo is not filled)
                try:
                    file_type = item.another_photo.url.split('.')[-1]
                    file_type = file_type.lower()
                    if file_type not in IMAGE_FILE_TYPES:
                        context = {
                            'form': form,
                            'error_message': 'Image file type must be PNG, JPG or JPEG',
                        }
                        return render(request, 'mainApp/update_item.html', context)
                except (ValueError):
                    pass

                # try except - error handling (request.FILES has ValueError if and_another_photo is not filled)
                try:
                    file_type = item.and_another_photo.url.split('.')[-1]
                    file_type = file_type.lower()
                    if file_type not in IMAGE_FILE_TYPES:
                        context = {
                            'form': form,
                            'error_message': 'Image file type must be PNG, JPG or JPEG',
                        }
                        return render(request, 'mainApp/update_item.html', context)
                except (ValueError):
                    pass

                item.photo_width, item.photo_height = get_image_dimensions(item.photo)
                item.compress_image_save()

                # remove the old photos
                image_path = settings.MEDIA_ROOT + '/' + photo_old.name
                if os.path.isfile(image_path):
                    os.remove(image_path)

                image_path = settings.MEDIA_ROOT + '/' + another_photo_old.name
                if os.path.isfile(image_path):
                    os.remove(image_path)

                image_path = settings.MEDIA_ROOT + '/' + and_another_photo_old.name
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


def item_available(request, item_id):
    if not request.user.is_authenticated:
        return redirect('mainApp:login_user')
    else:
        item = Item.objects.get(pk=item_id)
        if item.user == request.user:
            item.availability = 1
            item.save()
        items = Item.objects.filter(user=request.user)
        return render(request, 'mainApp/my_items.html', {'items': items})


def item_unavailable(request, item_id):
    if not request.user.is_authenticated:
        return redirect('mainApp:login_user')
    else:
        item = Item.objects.get(pk=item_id)
        if item.user == request.user:
            item.availability = 0
            item.save()
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


def login_main(request):
    if request.user.is_authenticated:
        return redirect('mainApp:index')
    else:
        return render(request, 'mainApp/login.html')


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
                    return render(request, 'mainApp/login_user.html', {'error_message': 'Your account has been disabled.'})
            else:
                return render(request, 'mainApp/login_user.html', {'error_message': 'Invalid login! Please contact us for help if you forget your password.'})
        return render(request, 'mainApp/login_user.html')


def logout_user(request):
    logout(request)
    return redirect('mainApp:index')



