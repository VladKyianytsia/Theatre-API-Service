import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play, Performance, Ticket, Reservation
from theatre.tests.test_theatre_hall_view_set import sample_theatre_hall

RESERVATION_URL = reverse("theatre:reservation-list")


class UnauthenticatedReservationViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(RESERVATION_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedReservationViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test12345"
        )
        self.client.force_authenticate(self.user)

    def test_create_reservation(self):
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
        ticket_data = {
            "seat": 1,
            "row": 1,
            "performance": performance.id
        }
        reservation_data = {
            "tickets": [ticket_data]
        }

        response = self.client.post(
            RESERVATION_URL,
            reservation_data,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Ticket.objects.all().exists())
        self.assertEqual(Reservation.objects.get(id=1).user, self.user)
