from django.contrib.auth import (
    get_user_model,
    authenticate,
    )

from django.utils.translation import gettext as _
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password' : {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """Create and return user with an encrypted password

        Args:
            validated_data (_type_): _description_

        Returns:
            _type_: user 
        """
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and validate user

        Args:
            instance (_type_): _description_
            validated_data (_type_): _description_

        Raises:
            serializers.ValidationError: _description_

        Returns:
            _type_: _description_
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """User auth token

    """

    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    def validate(self, attributes):
        email = attributes.get('email')
        password = attributes.get('password')
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )

        if not user:
            msg = _("Unable to authenticate with credentials")
            raise serializers.ValidationError(msg, code='authorization')

        attributes['user'] = user
        return attributes
