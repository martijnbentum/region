from django.urls import include,path,re_path

from . import views


app_name = 'catalogue'
urlpatterns = [
	path('',views.TextView.as_view(),name='text_view'),
	path('add_text/', views.add_text, name='add_text'),
	path('text/',views.TextView.as_view(),name='text_view'),
]
