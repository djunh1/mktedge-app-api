"""API Views

"""
from rest_framework import generics

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create new user

    Args:
        generics (_type_): _description_
    """

    serializer_class = UserSerializer
