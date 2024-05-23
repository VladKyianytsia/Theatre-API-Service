import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play, Performance
from theatre.serializers import PerformanceDetailSerializer
from theatre.tests.test_theatre_hall_view_set import sample_theatre_hall

PERFORMANCE_URL = reverse("theatre:performance-list")


class UnauthenticatedPerformanceViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PERFORMANCE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPerformanceViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_performance(self):
        play = Play.objects.create(
            title="test",
            description="testtest"
        )
        theatre_hall = sample_theatre_hall()
        performance = Performance.objects.create(
            play=play,
            theatre_hall=theatre_hall,
            show_time=datetime.datetime.now()
        )

        response = self.client.get(
            reverse("theatre:performance-detail", args=[performance.id])
        )

        serializer = PerformanceDetailSerializer(performance)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_performance_forbidden(self):
        play = Play.objects.create(
            title="test",
            description="testtest"
        )
        theatre_hall = sample_theatre_hall()

        response = self.client.post(
            PERFORMANCE_URL,
            {
                "play": play.id,
                "theatre_hall": theatre_hall.id,
                "show_time": datetime.datetime.now()
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_date(self):
        play = Play.objects.create(
            title="test",
            description="testtest"
        )
        theatre_hall = sample_theatre_hall()

        performance1 = Performance.objects.create(
            play=play,
            theatre_hall=theatre_hall,
            show_time="2024-03-29"
        )
        performance2 = Performance.objects.create(
            play=play,
            theatre_hall=theatre_hall,
            show_time="2024-03-30"
        )

        response = self.client.get(PERFORMANCE_URL, {"date": "2024-03-29"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_play(self):
        play1 = Play.objects.create(
            title="test1",
            description="testtest"
        )
        play2 = Play.objects.create(
            title="test2",
            description="testtest"
        )
        theatre_hall = sample_theatre_hall()

        performance1 = Performance.objects.create(
            play=play1,
            theatre_hall=theatre_hall,
            show_time=datetime.datetime.now()
        )
        performance2 = Performance.objects.create(
            play=play2,
            theatre_hall=theatre_hall,
            show_time=datetime.datetime.now()
        )

        response = self.client.get(PERFORMANCE_URL, {"play": f"{play1.id}"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class AdminPerformanceViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_performance(self):
        play = Play.objects.create(
            title="test",
            description="testtest"
        )
        theatre_hall = sample_theatre_hall()

        response = self.client.post(
            PERFORMANCE_URL,
            {
                "play": play.id,
                "theatre_hall": theatre_hall.id,
                "show_time": datetime.datetime.now()
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Performance.objects.filter(play_id=play.id).exists())
