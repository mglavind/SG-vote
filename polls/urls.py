from django.urls import path

from . import views
from django.contrib.auth import views as auth_views
from polls.views import ResetPasswordView
from django.contrib.auth.decorators import login_required

app_name = 'polls'
urlpatterns = [
    #path('', views.IndexView.as_view(), name='index'),
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('login_user/', views.login_user, name="login_user"),
    path('logout_user/', views.logout_user, name='logout_user'),
    path('register_user/', views.register_user, name='register_user'),
    path('password-reset', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='polls/password_reset_confirm.html'),
        name='password_reset_confirm'),
    path('password-reset-complete/',
        auth_views.PasswordResetCompleteView.as_view(template_name='polls/password_reset_complete.html'),
        name='password_reset_complete'),

    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    path('<int:question_id>/vote/', views.vote, name='vote'),




]
