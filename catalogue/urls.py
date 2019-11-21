from django.urls import include,path,re_path

from . import views

app_name = 'catalogue'
urlpatterns = [
	path('', views.PersonView.as_view(), name='person_view'),
	path('person/',views.PersonView.as_view(),name='person_view'),
	path('location/',views.get_locationname, 'location_name'),
	path('location_name/', views.get_locationname, name='location_name'),
	path('add_person/', views.add_person, name='add_person'),
	re_path(r'^select2/', include('django_select2.urls')),
	# path('location_name', views.get_locationname, name='location_name'),
]
