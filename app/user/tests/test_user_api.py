from venv import create
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse


from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
SELF_URL = reverse('user:me')

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):

    def setup(self):
        self.client = APIClient()


    def test_create_user_success(self):
        payload = {
            'email': 'oktoberfest@example.com',
            'password' : 'Wiesen123',
            'name' : 'Beer Hall Putsch',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_email_exists_error(self):
        payload = {
            'email': 'oktoberfest@example.com',
            'password' : 'Wiesen123',
            'name' : 'Fake Putsch',
        }

        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_too_short_error(self):
        payload = {
            'email': 'oktoberfest@example.com',
            'password' : 'abc',
            'name' : 'A name',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_user_token(self):
        user_details = {
            'name': 'Tressor',
            'email': 'Tressor@example.com',
            'password': 'testPassword123'
        }

        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password' : user_details['password'],
            'name' : user_details['name']
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_bad_user_token(self):
        user_details = {
            'name': 'Tressor',
            'email': 'Tressor@example.com',
            'password': 'testPassword123'
        }

        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password' : 'badPassword',
            'name' : user_details['name']
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_token_blank_password(self):
        user_details = {
            'name': 'Tressor',
            'email': 'Tressor@example.com',
            'password': ''
        }

        payload = {
            'email': user_details['email'],
            'password' : '',
            'name' : user_details['name']
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(SELF_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):

    def setUp(self):
        self.user = create_user(
            name ='Berghain',
            email ='Tressor@example.com',
            password = 'testPassword324',
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_success_profile(self):
        res = self.client.get(SELF_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
        })

    def test_post_to_self_not_allowed(self):
        res = self.client.post(SELF_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_update_user_profile(self):
        payload = {
            'name': 'updatedName',
            'password': 'newPassword324'
        }

        res = self.client.patch(SELF_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)










