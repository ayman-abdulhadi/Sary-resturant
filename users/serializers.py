from rest_framework import serializers
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ['employee_number', 'password', 'name', 'role']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 6},
            }

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
