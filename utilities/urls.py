from django.urls import include,path,re_path

from . import views


app_name = 'utilities'
urlpatterns = [
	path('close/',views.close,name='close'),
]
