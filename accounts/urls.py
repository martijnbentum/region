from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
 	path('', views.index, name='auth_index'),
 	path('register', views.RegisterView.as_view(), name='register'),
	path('edit_profile', views.UserEditView.as_view(), name='edit_profile'),
	path('change_password', views.PasswordsChangeView.as_view(), name='change_password'),
	path('log',views.log_view,name='log_view'),
	path('logs',views.logs_view,name='logs_view'),
	]
