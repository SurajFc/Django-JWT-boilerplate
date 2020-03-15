from rest_framework import serializers
from .models import (
    User, ContactUs
)


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('fname', 'lname', 'email', 'mobile',
                  'password')

    def create(self, validated_data):

        user = User.objects.create_user(
            fname=validated_data['fname'],
            lname=validated_data['lname'],
            email=validated_data['email'],
            mobile=validated_data.get('mobile', '')
        )

        # hashing the password
        user.set_password(validated_data['password'])
        user.save()
        return user


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'
