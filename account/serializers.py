from rest_framework import serializers
from .models import (
    User, Address,ContactUs
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
                  'password', 'account_type')

    def create(self, validated_data):

        user = User.objects.create_user(
            fname=validated_data['fname'],
            lname=validated_data['lname'],
            email=validated_data['email'],
            mobile=validated_data.get('mobile', ''),
            account_type=validated_data['account_type']
        )

        # hashing the password
        user.set_password(validated_data['password'])
        user.save()
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ('user',)

class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = '__all__'