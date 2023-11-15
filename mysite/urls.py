"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', include('polls.urls')),  # Include 'polls' app's URLs at the root path
    path('', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),

]

admin.site.site_header = 'SG Vote'
admin.site.index_title = 'Stemmetæller'                 # default: "Site administration"
admin.site.site_title = 'Stemmeoptæller' # default: "Django site admin"
