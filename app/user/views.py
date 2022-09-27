"""API Views

"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create new user

    Args:
        generics (_type_): _description_
    """

    serializer_class = UserSerializer

class CreateTokenView(ObtainAuthToken):
    """New token for user

    Args:
        ObtainAuthToken (_type_): _description_
    """
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage authenticated user

    Args:
        generics (_type_): _description_
    """
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Fetch authenticated user

        Returns:
            user: authenticated user object
        """
        return self.request.user

