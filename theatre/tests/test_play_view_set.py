from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Genre, Play
from theatre.serializers import PlayListSerializer, PlayDetailSerializer
from theatre.tests.test_actor_view_set import sample_actor

PLAY_URL = reverse("theatre:play-list")


class UnauthenticatedPlayViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(PLAY_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345"
        )
        self.client.force_authenticate(self.user)

    def test_list_plays(self):
        genre = Genre.objects.create(name="test")
        actor = sample_actor()

        play = Play.objects.create(
            title="test",
            description="testtest"
        )
        play.actors.add(actor.id)
        play.genres.add(genre.id)

        response = self.client.get(PLAY_URL)

        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve_play(self):
        genre = Genre.objects.create(name="test")
        actor = sample_actor()

        play = Play.objects.create(
            title="test",
            description="testtest"
        )
        play.actors.add(actor.id)
        play.genres.add(genre.id)

        response = self.client.get(
            reverse("theatre:play-detail", args=[play.id])
        )
        serializer = PlayDetailSerializer(play)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_play_forbidden(self):
        genre = Genre.objects.create(name="test")
        actor = sample_actor()

        response = self.client.post(
            PLAY_URL,
            {
                "title": "test",
                "description": "testtest",
                "genres": genre.id,
                "actors": actor.id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_title(self):
        play1 = Play.objects.create(
            title="test1",
            description="testtest",
        )

        play2 = Play.objects.create(
            title="test2",
            description="testtest"
        )

        response = self.client.get(PLAY_URL, {"title": "test1"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_filter_by_genre(self):
        play1 = Play.objects.create(
            title="test1",
            description="testtest",
        )

        play2 = Play.objects.create(
            title="test2",
            description="testtest"
        )
        play3 = Play.objects.create(
            title="test3",
            description="testtest"
        )

        genre1 = Genre.objects.create(name="genre1")
        genre2 = Genre.objects.create(name="genre2")

        play1.genres.add(genre1)
        play2.genres.add(genre2)

        response = self.client.get(
            PLAY_URL,
            {"genres": f"{genre1.id},{genre2.id}"}
        )

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)

    def test_filter_by_actor(self):
        play1 = Play.objects.create(
            title="test1",
            description="testtest",
        )

        play2 = Play.objects.create(
            title="test2",
            description="testtest"
        )
        play3 = Play.objects.create(
            title="test3",
            description="testtest"
        )

        actor1 = sample_actor()
        actor2 = sample_actor()

        play1.actors.add(actor1)
        play2.actors.add(actor2)

        response = self.client.get(
            PLAY_URL,
            {"actors": f"{actor1.id},{actor2.id}"}
        )

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, response.data)
        self.assertIn(serializer2.data, response.data)
        self.assertNotIn(serializer3.data, response.data)


class AdminPlayViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_play(self):
        actor = sample_actor()
        genre = Genre.objects.create(name="testgenre")
        response = self.client.post(
            PLAY_URL,
            {
                "title": "test",
                "description": "testtest",
                "actors": actor.id,
                "genres": genre.id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Play.objects.filter(title="test").exists())
