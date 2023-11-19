from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from habit.models import Place, Action
from habit.pagination import PlacePagination, ActionPagination
from habit.serializers import PlaceSerializer, ActionSerializer


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
