from django.conf.urls import url
from . import views

app_name = 'listing'

urlpatterns = [
    # /listing/
    url(r'^$', views.index, name='index'),

    # /listing/
    url(r'^visitor/$', views.index_visitor, name='index_visitor'),

    # /listing/register/
    url(r'^register/$', views.register, name='register'),

    # /listing/login_user/
    url(r'^login_user/$', views.login_user, name='login_user'),

    # /listing/logout_user/
    url(r'^logout_user/$', views.logout_user, name='logout_user'),

    # /listing/<city_id>/
    url(r'^(?P<item_id>[0-9]+)/detail/$', views.detail, name='detail'),

    # /listing/item/add/
    url(r'^add_item/$', views.add_item, name='add_item'),

    # /listing/
    url(r'^my_items/$', views.my_items, name='my_items'),

    # /listing/item/<city_id>/
    url(r'^(?P<item_id>[0-9]+)/update_item/$', views.update_item, name='update_item'),

    # /listing/item/<city_id>/delete/
    url(r'^(?P<item_id>[0-9]+)/delete_item/$', views.delete_item, name='delete_item'),

]