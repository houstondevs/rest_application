from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from phonenumber_field.modelfields import PhoneNumberField


User = get_user_model()


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=128, validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField(required=True, max_length=64)
    last_name = serializers.CharField(required=True, max_length=64)
    phone_number = serializers.CharField(required=True, validators=PhoneNumberField().validators)
    password1 = serializers.CharField(style={'input_type': 'password'},min_length=8, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, min_length=8, write_only=True)

    def validate(self, data):
        if User.objects.filter(phone_number=data['phone_number']).exists():
            raise serializers.ValidationError(_("User with this phone already exists!"))
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
            'password1': self.validated_data.get('password1', ''),
        }
    
    def save(self, request):
        self.cleaned_data = self.get_cleaned_data()
        user = User.objects.create_user(self.cleaned_data['email'], self.cleaned_data['first_name'], self.cleaned_data['last_name'],self.cleaned_data['phone_number'],self.cleaned_data['password1'])
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'email', 'phone_number', 'first_name', 'last_name')
        read_only_fields = ('pk',)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'email', 'phone_number', 'first_name', 'last_name')
        read_only_fields = ('pk',)


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={'input_type': 'password'},min_length=8)
    new_password1 = serializers.CharField(style={'input_type': 'password'},min_length=8)
    new_password2 = serializers.CharField(style={'input_type': 'password'},min_length=8)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError(_("Новые пароли не совпадают!"))
        return data


class UserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=128)


class UserPasswordResetConfirmSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(style={'input_type': 'password'},min_length=8)
    new_password2 = serializers.CharField(style={'input_type': 'password'},min_length=8)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError(_("Новые пароли не совпадают!"))
        return data