import pytz
import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule

from config import settings


def set_schedule(habit):
    if not habit.is_pleasure:
        target_timezone = pytz.timezone(settings.TIME_ZONE)
        converted_datetime = habit.time.astimezone(target_timezone)

        schedule, created = IntervalSchedule.objects.get_or_create(
            every=habit.periodicity,
            period=IntervalSchedule.MINUTES,
        )
        PeriodicTask.objects.create(
            interval=schedule,
            name=str(habit.pk),
            task='habits.tasks.send_telegram_message',
            kwargs=json.dumps({
                'chat_id': habit.owner.telegram_chat_id,
                'action': habit.action.name,
                'time': str(converted_datetime.time().replace(second=0, microsecond=0)),
                'place': habit.place.name
            })
        )


def delete_schedule(habit_pk):
    if PeriodicTask.objects.filter(name=str(habit_pk)).exists():
        periodic_task = PeriodicTask.objects.get(name=str(habit_pk))
        periodic_task.delete()
