from datetime import datetime

from django.contrib.auth import get_user_model

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from rest_framework.test import APIClient
from rest_framework import status

from cinema.models import (
    CinemaHall,
    MovieSession,
    Movie,
    Genre,
    Actor
)
from cinema.serializers import MovieSessionListSerializer

BASE_URL = reverse("cinema:moviesession-list")
DETAIL_URL = reverse("cinema:moviesession-detail", kwargs={"pk": 1})


def sample_movie(**params):
    defaults = {
        "title": "Sample movie",
        "description": "Sample description",
        "duration": 90,
    }
    defaults.update(params)

    return Movie.objects.create(**defaults)

def sample_genre(**params):
    defaults = {
        "name": "Drama",
    }
    defaults.update(params)

    return Genre.objects.create(**defaults)

def sample_actor(**params):
    defaults = {"first_name": "George", "last_name": "Clooney"}
    defaults.update(params)

    return Actor.objects.create(**defaults)

def sample_movie_session(**params):
    cinema_hall = CinemaHall.objects.create(
        name="Blue", rows=20, seats_in_row=20
    )
    movie = sample_movie(**params)

    defaults = {
        "show_time": timezone.make_aware(datetime(2022, 6, 2, 14, 0)),
        "movie": movie,
        "cinema_hall": cinema_hall,
    }
    defaults.update(params)

    return MovieSession.objects.create(**defaults)


class UnAthorizedAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unathorized_api(self):
        response = self.client.get(DETAIL_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@user.test",
            password="passworduser"
        )
        self.client.force_authenticate(self.user)
        self.movie = sample_movie()
        self.genre = sample_genre()
        self.actor = sample_actor()

    def test_movie_session_list(self):
        queryset = MovieSession.objects.all()
        response = self.client.get(BASE_URL)
        serializer = MovieSessionListSerializer(queryset, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)
