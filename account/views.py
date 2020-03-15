import requests
import ast
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_text
from .tokens import account_activation_token
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .prevents import UserLoginRateThrottle
from .serializers import (
    RegistrationSerializer, AddressSerializer, ContactUsSerializer
)
from .models import (
    User, Address, ContactUs
)
from django.contrib.auth.models import update_last_login
from django.http import HttpResponse
from django.contrib.auth import authenticate
from lyne.authorization import GetUserFromToken
import json
import os
from .baseclass import AbstractBaseClassApiView
from .tasks import mysendmail


# generating JWT
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# Register
class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            x = serializer.save()
            site = get_current_site(request)
            y = str(x.user_id)
            mysendmail.delay(str(site.domain), y)  # sendingmail using celery
            ser = AddressSerializer(data=request.data)
            ser.is_valid()
            ser.save(user=x)
            return Response("Account Created..", status=status.HTTP_201_CREATED)
        return Response(serializer.errors)

# Account Activation


class ActivateAccount(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_confirmed = True
            user.save()

            return Response("Activated")
        else:
            return Response("Already activated")


# login User
class LoginView(APIView):
    permission_classes = (AllowAny,)
    throttle_classes = (UserLoginRateThrottle,)

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        try:
            user = authenticate(username=email, password=password)
            if User.objects.get(email=email) is None:
                return Response({"msg": "No Account found with this mail", "status": "0"})

            if user is not None and user.is_confirmed and user.is_active:
                update_last_login(None, user)
                token = get_tokens_for_user(user)
                access_token = token['access']
                context = {
                    'fname': user.fname,
                    'lname': user.lname,
                    'user_id': user.user_id,
                    'token': access_token
                }

                dump = json.dumps(context)
                response = HttpResponse(dump, content_type="application/json")
                response.set_cookie('cookie', token, httponly=True)
                response.set_cookie('user', user.user_id, httponly=True)
                return response
            else:
                return Response("Account is not activated or Wrong Password", status=status.HTTP_400_BAD_REQUEST)
        except:
            print("ehey")
            return Response("Wrong")


# logout
class LogoutView(APIView):

    def get(self, request):
        token_cookie = request.COOKIES.get('cookie')  # reading cookie
        # accessing value of the cookie
        token_read = ast.literal_eval(token_cookie)
        refresh = token_read['refresh']
        token = RefreshToken(refresh)
        token.blacklist()  # blacklisting the token
        context = {
            'msg': 'Logout Successfully',
            'status': '1'
        }

        dump = json.dumps(context)
        response = HttpResponse(dump, content_type="application/json")
        response.delete_cookie('cookie')
        response.delete_cookie('user')
        return response


# Read Cookie
# To be the first api to be called on every Reload of spa...
class ReadCookie(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        if request.COOKIES.get('cookie'):
            x = request.COOKIES.get('cookie')
            x = ast.literal_eval(x)
            payload = {'token': x['refresh']}
            host = request.META['HTTP_HOST']
            url = f"http://{host}/tokenverify"
            resp = requests.post(url, data=payload)
            val = resp.json()
            if val == {}:
                if request.COOKIES.get('user'):
                    user = request.COOKIES.get('user')
                    user = User.objects.get(user_id=user)
                    payload = {'token': x['access']}
                    host = request.META['HTTP_HOST']
                    url = f"http://{host}/tokenverify"
                    resp = requests.post(url, data=payload)
                    val = resp.json()
                    if val == {}:
                        return Response({"msg": "Token is Valid", "token": x['access'], "status": "2"})

                    else:
                        token = get_tokens_for_user(user)
                        access_token = token['access']
                        context = {
                            'fname': user.fname,
                            'lname': user.lname,
                            'user_id': user.user_id,
                            'token': access_token,
                            'status': '1'
                        }

                        dump = json.dumps(context)
                        response = HttpResponse(
                            dump, content_type="application/json")
                        response.set_cookie('cookie', token, httponly=True)
                        return response
                else:
                    context = {
                        "msg": "Token is InValid. Relogin",
                        "status": "0"
                    }
                    dump = json.dumps(context)
                    response = HttpResponse(
                        dump, content_type="application/json")
                    response.delete_cookie('cookie', token, httponly=True)
                    return response

            else:
                return Response({"msg": "Token is InValid. Relogin", "status": "0"}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"msg": "Token is InValid. Relogin", "status": "0"}, status.HTTP_400_BAD_REQUEST)


class ContactUsView(AbstractBaseClassApiView):
    permission_classes = (AllowAny,)
    throttle_classes = (UserLoginRateThrottle,)
    serializer_class = ContactUsSerializer
    http_method_names = ['post']
