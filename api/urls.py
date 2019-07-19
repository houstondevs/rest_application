from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from app_accounts.views import RegistrationView, activate, UsersView, UserDetailView, UserPasswordChangeView, UserPasswordResetView, UserPasswordResetConfirmView
from app_blog.views import (PostView, TagView)

router = DefaultRouter()

router.register('users', UsersView)
router.register('posts', PostView)
router.register('tags', TagView)

urlpatterns = [
    path('account/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('account/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('account/me/', UserDetailView.as_view(), name='account_detail'),
    path('account/create/', RegistrationView.as_view(), name='registration'),
    path('account/activate/<uidb64>/<token>/', activate, name='activate'),
    path('account/password/change/', UserPasswordChangeView.as_view(), name="change_password"),
    path('account/password/reset/', UserPasswordResetView.as_view(), name="reset_password"),
    path('account/password/reset/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name="reset_password_confirm"),
    

    path('', include(router.urls)),

    path('api-auth/', include('rest_framework.urls')),
]