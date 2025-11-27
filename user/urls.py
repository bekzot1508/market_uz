from django.urls import path
from user.views import RegisterView, LoginView, ProfileView, LogoutView, ProfileUpdateView, MyPasswordChangeView, \
    MyPasswordChangeDoneView

app_name = 'user'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Password change
    path('password-change/', MyPasswordChangeView.as_view(), name='password_change'),
    path('password-change-done/', MyPasswordChangeDoneView.as_view(), name='password_change_done'),

    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit', ProfileUpdateView.as_view(), name='profile_edit'),
]
