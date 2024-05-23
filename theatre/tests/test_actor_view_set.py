from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Actor
from theatre.serializers import ActorSerializer

ACTOR_URL = reverse("theatre:actor-list")


def sample_actor(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Smith"
    }
    defaults.update(params)

    return Actor.objects.create(**defaults)


class UnauthenticatedActorViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(ACTOR_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedActorViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345"
        )
        self.client.force_authenticate(self.user)

    def test_list_actors(self):
        sample_actor()
        sample_actor()

        response = self.client.get(ACTOR_URL)

        actors = Actor.objects.all()
        serializer = ActorSerializer(actors, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_actor_forbidden(self):
        response = self.client.post(
            ACTOR_URL,
            {
                "first_name": "John",
                "last_name": "Smith"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminActorViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_actor(self):
        response = self.client.post(
            ACTOR_URL,
            {
                "first_name": "John",
                "last_name": "Smith"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Actor.objects.filter(first_name="John").exists())
