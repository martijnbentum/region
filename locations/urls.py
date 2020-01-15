from django.urls import include,path,re_path

from . import views


app_name = 'locations'
urlpatterns = [
	path('add_location/',views.add_location, name='add_location'),
	path('map/<str:location_name>/',views.map, name='map'),
	path('world',views.world, name='world'),
	path('add_userloc/<str:location_name>/',views.add_userloc,name='add_userloc'),
	path('',views.LocationView.as_view(),name='location_view'),
]