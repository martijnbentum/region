from django.urls import include,path,re_path

from . import views


app_name = 'locations'
urlpatterns = [
	path('map/<str:location_name>/',views.mapp, name='mapp'),
	path('',views.location_list,name='location_list'),
	path('delete/<int:pk>/<str:model_name>', views.delete, name='delete'),
	path('location/', views.location_list, name='location_list'),
	path('add_location/', views.edit_location, name='add_location'),
	path('add_location/<str:view>', views.edit_location, name='add_location'),
	path('edit_location/<int:pk>', views.edit_location, name='edit_location'),
	path('edit_location/<int:pk>/<str:focus>', views.edit_location, name='edit_location'),
]
