from django.urls import path
from rest_framework import routers
from habit.apps import HabitConfig
from habit.views import PlaceViewSet, ActionViewSet

app_name = HabitConfig.name

router = routers.DefaultRouter()
router.register('places', PlaceViewSet, basename='places')
router.register('actions', ActionViewSet, basename='actions')

urlpatterns = [

] + router.urls
