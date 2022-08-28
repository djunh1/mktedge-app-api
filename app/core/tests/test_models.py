
"""
Tests for models.

DJacobson 8/27/2022
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):

    def test_create_user_with_email_success(self):
        email = "unassisted@example.com"
        password = 'pastalavista'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_new_user_email_normalized(self):
        sample_emails = [
            ['bergeron@EXAMPLE.com', 'bergeron@example.com'],
            ['Pasternak@Example.com', 'Pasternak@example.com'],
            ['MARCHAND@EXAMPLE.COM', 'MARCHAND@example.com'],
            ['krecji@example.COM', 'krecji@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'hatTrick345')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_exception(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test234')

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            'ribbentrop@example.com',
            'test2345'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
