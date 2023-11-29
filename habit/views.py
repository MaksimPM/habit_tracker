from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated

from habit.models import Place, Action, Habit
from habit.pagination import PlacePagination, ActionPagination, HabitPagination
from habit.permissions import IsUserOrStaff
from habit.serializers import PlaceSerializer, ActionSerializer, HabitSerializer
from habit.services import set_schedule, delete_schedule


class PlaceViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    pagination_class = PlacePagination


class ActionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    pagination_class = ActionPagination


class HabitCreateAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = HabitSerializer

    def perform_create(self, serializer, **kwargs):
        new_habit = serializer.save()
        new_habit.owner = self.request.user
        new_habit.save()

        set_schedule(habit=new_habit)


class HabitListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = HabitSerializer
    pagination_class = HabitPagination

    def get_queryset(self):
        queryset = Habit.objects.filter(owner=self.request.user)
        return queryset


class HabitPublicListAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Habit.objects.filter(is_public=True)
    serializer_class = HabitSerializer
    pagination_class = HabitPagination


class HabitRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsUserOrStaff,)
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer


class HabitUpdateAPIView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsUserOrStaff,)
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def perform_update(self, serializer):
        habit = serializer.save()
        delete_schedule(habit_pk=habit.pk)
        set_schedule(habit=habit)


class HabitDestroyAPIView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsUserOrStaff,)
    queryset = Habit.objects.all()
    serializer_class = HabitSerializer

    def perform_destroy(self, instance):
        delete_schedule(habit_pk=instance.pk)
        super().perform_destroy(instance)
