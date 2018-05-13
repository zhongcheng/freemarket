from django.conf.urls import url
from . import views
from .recaptcha import check_recaptcha

app_name = 'listing'

urlpatterns = [
    # /
    url(r'^$', views.index, name='index'),

    # /visitor/
    url(r'^visitor/$', views.index_visitor, name='index_visitor'),

    # /register/
    url(r'^register/$', check_recaptcha(views.register), name='register'),

    # /my_info/
    url(r'^my_info/$', views.my_info, name='my_info'),

    # /login_user/
    url(r'^login_user/$', check_recaptcha(views.login_user), name='login_user'),

    # /logout_user/
    url(r'^logout_user/$', views.logout_user, name='logout_user'),

    # /<item_id>/detail/
    url(r'^(?P<item_id>[0-9]+)/detail/$', views.detail, name='detail'),

    # /add_item/
    url(r'^add_item/$', views.add_item, name='add_item'),

    # /my_item/
    url(r'^my_items/$', views.my_items, name='my_items'),

    # /<item_id>/update_item/
    url(r'^(?P<item_id>[0-9]+)/update_item/$', views.update_item, name='update_item'),

    # /<item_id>/delete_item/
    url(r'^(?P<item_id>[0-9]+)/delete_item/$', views.delete_item, name='delete_item'),

]