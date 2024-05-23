from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import TheatreHall
from theatre.serializers import TheatreHallSerializer

THEATRE_URL = reverse("theatre:theatrehall-list")


def sample_theatre_hall(**params):
    defaults = {
        "name": "test",
        "rows": 5,
        "seats_in_row": 5
    }
    defaults.update(params)

    return TheatreHall.objects.create(**defaults)


class UnauthenticatedTheatreHallViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(THEATRE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTheatreHallViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345"
        )
        self.client.force_authenticate(self.user)

    def test_list_theatre_halls(self):
        sample_theatre_hall()
        sample_theatre_hall()

        response = self.client.get(THEATRE_URL)

        theatre_halls = TheatreHall.objects.all()
        serializer = TheatreHallSerializer(theatre_halls, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_theatre_hall_forbidden(self):
        response = self.client.post(
            THEATRE_URL,
            {
                "name": "test",
                "rows": 5,
                "seats_in_row": 5
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminTheatreHallViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_theatre_hall(self):
        response = self.client.post(
            THEATRE_URL,
            {
                "name": "test",
                "rows": 5,
                "seats_in_row": 5
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            TheatreHall.objects.filter(name=response.data["name"]).exists()
        )
