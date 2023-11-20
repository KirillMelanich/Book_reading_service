from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "full_name", "email")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name", "email", "password")
        read_only_fields = ("id", "is_stuff")
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """create user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update user with corrected encrypted password"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user
