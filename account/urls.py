from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from .views import (
    RegisterView, ActivateAccount,LoginView,LogoutView,
    ReadCookie,ContactUsView
)


urlpatterns = [
    path('register', RegisterView.as_view()),  # user Register
    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(),
         name='activate'),  # user Activate
    path('login',LoginView.as_view()), #Login
    path('logout',LogoutView.as_view()), #logout 
    path('contactus',ContactUsView.as_view()),
    path('tokenverify', TokenVerifyView.as_view(), name='token_verify'),  #for verifying token 
    path("read_cookie",ReadCookie.as_view()),   #<------ Read Cookies (Pls read readme.md)
]