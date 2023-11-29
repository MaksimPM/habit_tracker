from rest_framework.serializers import ValidationError

from habit.models import Habit


class RewardValidator:
    def __init__(self, fields_list):
        self.fields = fields_list

    def __call__(self, value):
        print(value)
        if not value.get('is_pleasure'):
            if not value.get(self.fields[0]) and not value.get(self.fields[1]):
                raise ValidationError("У привычки должно быть вознаграждение или связанная привычка!")
            elif self.fields[0] in value and self.fields[1] in value:
                raise ValidationError("у привычки не может быть одновременно вознаграждения и связанной привычки!")


class TimeToCompleteValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if self.field in value and value.get(self.field) > 120:
            raise ValidationError("Время выполнения должно быть не больше 120 секунд!")


class PleasureHabitValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if value.get(self.field):
            habit_pk = dict(value).get(self.field).pk
            habit = Habit.objects.get(pk=habit_pk)
            if not habit.is_pleasure:
                raise ValidationError(
                    "В связанные привычки могут попадать только привычки с признаком приятной привычки!")


class IsPleasureValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if value.get(self.field):
            if 'pleasure_habit' in value or 'reward' in value:
                raise ValidationError("У приятной привычки не может быть вознаграждения или связанной привычки!")


class PeriodicityValidator:
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        if self.field in value and value.get(self.field) > 7:
            raise ValidationError("Нельзя выполнять привычку реже, чем 1 раз в 7 дней!")


def patch_validator(habit, validated_data):
    if 'is_pleasure' in validated_data:
        if habit.reward or habit.pleasure_habit:
            raise ValidationError(
                "У привычки есть вознаграждение или связанная привычка, поэтому она не может быть приятной!")
    if habit.reward and validated_data.get('pleasure_habit'):
        raise ValidationError("У привычки есть вознаграждение, у нее не может быть связанной привычки!")
    if habit.pleasure_habit and validated_data.get('reward'):
        raise ValidationError("У привычки есть связанная привычка, у нее не может быть вознаграждения!")