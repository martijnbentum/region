from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
 	path('', views.index, name='auth_index'),
 	path('register', views.RegisterView.as_view(), name='register')
	]
