from django.urls import path

from . import views

app_name = "properties"

urlpatterns = [
    path("", views.home, name="home"),
    path("properties/", views.property_list, name="list"),
    path("properties/<int:pk>/", views.property_detail, name="detail"),
    path("interest/<int:pk>/", views.express_interest, name="interest"),
    path("interest/complete/", views.complete_interest, name="complete_interest"),
    path("interest/sent/<int:pk>/", views.interest_sent, name="interest_sent"),
    path("my-interests/", views.my_interests, name="my_interests"),
    path("about/", views.about, name="about"),
]
