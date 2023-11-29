from django.urls import path
from rest_framework import routers
from habit.apps import HabitConfig
from habit.views import PlaceViewSet, ActionViewSet, HabitListAPIView, HabitPublicListAPIView, HabitCreateAPIView, \
    HabitRetrieveAPIView, HabitUpdateAPIView, HabitDestroyAPIView

app_name = HabitConfig.name

router = routers.DefaultRouter()
router.register(r'places', PlaceViewSet, basename='places')
router.register(r'actions', ActionViewSet, basename='actions')

urlpatterns = [
    path('habit/', HabitListAPIView.as_view(), name='habit_list'),
    path('habit/public/', HabitPublicListAPIView.as_view(), name='habit_public_list'),
    path('habit/create/', HabitCreateAPIView.as_view(), name='habits_list'),
    path('habit/<int:pk>/', HabitRetrieveAPIView.as_view(), name='habit'),
    path('habit/<int:pk>/update/', HabitUpdateAPIView.as_view(), name='habit_update'),
    path('habit/<int:pk>/delete/', HabitDestroyAPIView.as_view(), name='habit_delete'),
] + router.urls
