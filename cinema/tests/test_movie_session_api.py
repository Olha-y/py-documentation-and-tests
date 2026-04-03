import datetime
import tempfile
import os
from datetime import timedelta
from email.policy import default

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from cinema.models import CinemaHall, MovieSession, Movie, Genre, Actor
from cinema.serializers import MovieSessionSerializer, MovieSessionListSerializer

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
        "show_time": "2022-06-02 14:00:00",
        "movie": movie,
        "cinema_hall": cinema_hall,
    }
    defaults.update(params)

    return MovieSession.objects.create(**defaults)

def image_upload_url(movie_id):
    """Return URL for recipe image upload"""
    return reverse("cinema:movie-upload-image", args=[movie_id])

def detail_url(movie_id):
    return reverse("cinema:movie-detail", args=[movie_id])


class UnAthorizedAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unathorized_api(self):
        response = self.client.get(DETAIL_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email="user@user.test", password="passworduser")
        self.client.force_authenticate(self.user)
        self.movie = sample_movie()
        self.genre = sample_genre()
        self.actor = sample_actor()

    def test_movie_session_list(self):
        response = self.client.get(BASE_URL)
        movie_sessions = MovieSession.objects.all()
        serializer = MovieSessionListSerializer(movie_sessions, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
