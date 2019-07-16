from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import views

from .serializers import (RegistrationSerializer, UserListSerializer, UserDetailSerializer, UserChangePasswordSerializer, UserPasswordResetSerializer, UserPasswordResetConfirmSerializer)
from .tokens import account_activation_token, password_reset_token
from api.permissions import IsObjectOwner


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password1', 'password2')
)

User = get_user_model()


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def send_message(self, request, user, serializer):
        current_site = get_current_site(request)
        mail_subject = '{} - Активируйте свой аккаунт!'.format(current_site)
        message = render_to_string('registration/account_activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user),
        })
        to_email = serializer.data.get("email")
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(RegistrationView, self).dispatch(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        print(user.email, 2)
        self.send_message(request, user, serializer)
        headers = self.get_success_headers(serializer.data)

        return Response({'detail': 'Письмо с активацией было отправлено на вашу почту', 'user': serializer.data},
                        status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        return user


@api_view(['GET'])
def activate(request, uidb64, token):
    if request.method == 'GET':
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response('Спасибо за подтверждение почты! Теперь вы можете войти!')
        else:
            return Response('Ссылка на активацию больше не доступна!')


class UsersView(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 viewsets.GenericViewSet):
    serializer_class = UserListSerializer
    queryset = User.objects.all()
    permission_classes = (IsObjectOwner, permissions.IsAuthenticated)

        
class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = UserDetailSerializer

    def get_object(self):
        return self.request.user


class UserPasswordChangeView(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer(self, *args, **kwargs):
        return UserChangePasswordSerializer(*args, **kwargs)

    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            old_password = serializer.data.get("old_password")
            new_password2 = serializer.data.get('new_password2')
            if not self.object.check_password(old_password):
                return Response({"Старый пароль": ["Неверный пароль"]},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password2"))
            self.object.save()
            return Response({"Пароль изменен!"}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetView(views.APIView):
    permission_classes = (permissions.AllowAny, )

    def get_serializer(self, *args, **kwargs):
        return UserPasswordResetSerializer(*args, **kwargs)

    def send_message(self, request, user, serializer):
        current_site = get_current_site(request)
        mail_subject = '{} - Восстоновление пароля '.format(current_site)
        message = render_to_string('registration/account_reset_password.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': password_reset_token.make_token(user),
        })
        to_email = serializer.data.get("email")
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=serializer.data.get('email'))
            self.send_message(request, user, serializer)
            return Response({'detail': 'Письмо для восстановления пароля отправленно на вашу почту!'}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetConfirmView(views.APIView):
    permission_classes = (permissions.AllowAny, )

    def get_serializer(self, *args, **kwargs):
        return UserPasswordResetConfirmSerializer(*args, **kwargs)

    def get(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError):
            user = None

        if user is not None and password_reset_token.check_token(user, token):
            return Response({'detail':'Восстоновление пароля для {}'.format(user.email)})
        else:
            return Response({'detail':'Ссылка восстоновление больше не доступна!'})
        
            

    def post(self, request, uidb64, token):
        serializer = self.get_serializer(data=request.data)
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError):
            user = None

        if user is not None and password_reset_token.check_token(user, token):
            if serializer.is_valid():
                if user.check_password(serializer.data.get('new_password2')):
                    return Response({'detail':'Новый пароль не должен быть похож на старый!'},status=status.HTTP_400_BAD_REQUEST)
                user.set_password(serializer.data.get('new_password2'))
                user.save()
                return Response({'detail':'Пароль изменен!'})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail':'Ссылка на восстоновление больше не доступна!'})

            