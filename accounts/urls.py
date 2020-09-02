from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
 	path('', views.index, name='auth_index'),
 	path('register', views.RegisterView.as_view(), name='register'),
	path('log',views.log_view,name='log_view'),
	path('logs',views.logs_view,name='logs_view'),
	]
