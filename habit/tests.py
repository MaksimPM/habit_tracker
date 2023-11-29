import pytz

from django_celery_beat.models import PeriodicTask
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from config import settings
from habit.models import Place, Action, Habit
from habit.services import set_schedule, delete_schedule
from habit.tasks import send_telegram_message
from users.models import User


class HabitTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            email='test@test.ru',
            telegram_chat_id=settings.SUPERUSER_TELEGRAM_CHAT_ID,
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        self.user.set_password('0000')
        self.user.save()
        self.access_token = str(AccessToken.for_user(self.user))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.place = Place.objects.create(
            name='test_place',
        )

        self.action = Action.objects.create(
            name='test_action',
        )

        self.useful_habit = Habit.objects.create(
            owner=self.user,
            place=self.place,
            action=self.action,
            reward='yes'
        )

        self.pleasure_habit = Habit.objects.create(
            owner=self.user,
            place=self.place,
            action=self.action,
            is_pleasure=True
        )

    def test_create_place(self):
        data = {'name': 'new_test'}
        response = self.client.post('/places/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_place(self):
        places = list(Place.objects.all())
        response = self.client.get('/places/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(places))
        self.assertEqual(response.json()['results'][0]['id'], places[0].pk)

    def test_retrieve_place(self):
        response = self.client.get(f'/places/{self.place.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.place.pk)
        self.assertEqual(response.json()['name'], self.place.name)

    def test_update_place(self):
        data = {'name': 'new_test'}
        response = self.client.put(f'/places/{self.place.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], data.get('name'))
        response = self.client.patch(f'/places/{self.place.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], data.get('name'))

    def test_delete_place(self):
        response = self.client.delete(f'/places/{self.place.pk}')
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_create_action(self):
        data = {'name': 'new_test'}
        no_data = {}
        response = self.client.post('/actions/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], data.get('name'))
        self.assertTrue(Action.objects.filter(id=response.json()['id']).exists())
        response = self.client.post('/places/', no_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'name': ['Обязательное поле.']})

    def test_list_action(self):
        actions = list(Action.objects.all())
        response = self.client.get('/actions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], len(actions))
        self.assertEqual(response.json()['results'][0]['id'], actions[0].pk)

    def test_retrieve_action(self):
        response = self.client.get(f'/actions/{self.action.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.action.pk)
        self.assertEqual(response.json()['name'], self.action.name)

    def test_update_action(self):
        data = {'name': 'new_test'}
        response = self.client.put(f'/actions/{self.action.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], data.get('name'))
        response = self.client.patch(f'/actions/{self.action.pk}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], data.get('name'))

    def test_delete_action(self):
        response = self.client.delete(f'/actions/{self.action.pk}')
        self.assertEqual(response.status_code, status.HTTP_301_MOVED_PERMANENTLY)

    def test_create_habit(self):
        habit = {'place': self.place.pk, 'action': self.action.pk, 'pleasure_habit': self.pleasure_habit.pk,
                       'periodicity': 7, 'execution_time': 120}
        response = self.client.post('/habit/create/', habit)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Habit.objects.filter(id=response.json().get('id')).exists())
        self.assertTrue(PeriodicTask.objects.filter(name=response.json().get('id')).exists())

    def test_list_habit(self):
        response = self.client.get('/habit/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_habit(self):
        response = self.client.get(f'/habit/{self.useful_habit.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['id'], self.useful_habit.pk)

    def test_update_habit(self):
        data = {'reward': 'new_reward', 'periodicity': 3, 'execution_time': 90}
        response = self.client.patch(f'/habit/{self.useful_habit.pk}/update/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('reward'), data.get('reward'))
        self.assertEqual(response.json().get('periodicity'), data.get('periodicity'))
        self.assertEqual(response.json().get('execution_time'), data.get('execution_time'))

    def test_delete_habit(self):
        response = self.client.delete(f'/habit/{self.useful_habit.pk}/delete/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(pk=self.useful_habit.pk).exists())

    def test_list_public_habits(self):
        public_habits = Habit.objects.filter(is_public=True)
        response = self.client.get('/habit/public/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('count'), len(public_habits))

    def test_create_periodic_task(self):
        self.assertFalse(PeriodicTask.objects.filter(name=self.useful_habit.pk).exists())
        set_schedule(self.useful_habit)
        self.assertTrue(PeriodicTask.objects.filter(name=self.useful_habit.pk).exists())

    def test_delete_periodic_task(self):
        set_schedule(self.useful_habit)
        self.assertTrue(PeriodicTask.objects.filter(name=self.useful_habit.pk).exists())
        delete_schedule(self.useful_habit.pk)
        self.assertFalse(PeriodicTask.objects.filter(name=self.useful_habit.pk).exists())

    def test_send_telegram_message(self):
        target_timezone = pytz.timezone(settings.TIME_ZONE)
        converted_datetime = self.useful_habit.time.astimezone(target_timezone)
        kwargs = {
            'chat_id': self.useful_habit.owner.telegram_chat_id,
            'action': self.useful_habit.action.name,
            'time': str(converted_datetime.time().replace(second=0, microsecond=0)),
            'place': self.useful_habit.place.name
        }
        send_telegram_message.apply_async(kwargs=kwargs)
