from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
import jwt
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from account.models import User


class GetUserFromToken(object):
    def get_user(self, request):
        token1 = request.META['HTTP_AUTHORIZATION']
        token = token1.split(' ')[1]
        try:
            payload_decoded = jwt.decode(token, settings.SECRET_KEY)
            print('payload',   payload_decoded)
            user = payload_decoded['user_id']
            user = User.objects.get(user_id=user)
            return user
        except jwt.ExpiredSignatureError:
            return Response(status=440)