from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("login/", views.broker_login, name="login"),
    path("logout/", views.broker_logout, name="logout"),
    path("", views.home, name="home"),
    path("properties/", views.property_list, name="property_list"),
    path("properties/easy-add/", views.property_easy_add, name="property_easy_add"),
    path("properties/add/", views.property_create, name="property_add"),
    path("properties/<int:pk>/edit/", views.property_edit, name="property_edit"),
    path(
        "properties/<int:pk>/from-message/",
        views.property_apply_message,
        name="property_from_message",
    ),
    path("properties/<int:pk>/delete/", views.property_delete, name="property_delete"),
    path("images/<int:pk>/delete/", views.image_delete, name="image_delete"),
    path("images/<int:pk>/primary/", views.image_set_primary, name="image_set_primary"),
    path("interests/", views.interest_list, name="interest_list"),
    path("interests/<int:pk>/status/", views.interest_update_status, name="interest_status"),
]
