from django.urls import include,path,re_path

from . import views


app_name = 'locations'
urlpatterns = [
	path('add_location/',views.add_location, name='add_location'),
	path('add_location/<str:view>', views.add_location, 
		name='add_location'),
	path('add_location/<str:focus>/<str:view>/<int:pk>', views.add_location, 
		name='add_location'),
	path('add_location/<str:focus>/<int:pk>', views.add_location, 
		name='edit_location'),
	path('map/<str:location_name>/',views.mapp, name='mapp'),
	path('world',views.world, name='world'),
	path('germany',views.germany, name='germany'),
	path('add_userloc/<str:location_name>/',views.add_userloc,name='add_userloc'),
	path('',views.location_list,name='location_list'),
	path('location',views.location_list,name='location_list'),
	path('userloc/',views.location_list,name='location_list'),
	path('delete/<int:pk>/<str:model_name>', views.delete, name='delete'),
	path('geoloc/', views.geoloc_list, name='geoloc_list'),
	path('add_geoloc/', views.edit_geoloc, name='add_geoloc'),
	path('add_geoloc/<str:view>', views.edit_geoloc, name='add_geoloc'),
	path('edit_geoloc/<int:pk>', views.edit_geoloc, name='edit_geoloc'),
	path('edit_geoloc/<int:pk>/<str:focus>', views.edit_geoloc, name='edit_geoloc'),
	path('userloc/', views.location_list, name='userloc_list'),
	path('add_userloc/', views.edit_userloc, name='add_userloc'),
	path('add_userloc/<str:view>', views.edit_userloc, name='add_userloc'),
	path('edit_userloc/<int:pk>', views.edit_userloc, name='edit_userloc'),
	path('edit_userloc/<int:pk>/<str:focus>', views.edit_userloc, name='edit_userloc'),
]
