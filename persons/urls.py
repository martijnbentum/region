from django.urls import include,path,re_path

from . import views


app_name = 'persons'
urlpatterns = [
	path('', views.PersonView.as_view(), name='person_list'),
	path('movement_list', views.MovementView.as_view(), 
		name='movement_list'),
	path('add_person/', views.edit_person, name='add_person'),
	path('add_person/<str:view>', views.edit_person, name='add_person'),
	path('add_movement/', views.edit_movement, name='add_movement'),
	path('add_movement/<str:view>', views.edit_movement, 
		name='add_movement'),
	path('edit_person/<int:pk>', views.edit_person, name='edit_person'),
	path('edit_person/<int:pk>/<str:focus>', 
		views.edit_person, name='edit_person'),
	path('edit_movement/<int:pk>', views.edit_movement, 
		name='edit_movement'),
	path('edit_movement/<int:pk>/<str:focus>', views.edit_movement, 
		name='edit_movement'),
	path('person/<int:person_id>',views.person_detail,name='person_detail'),
	path('person/add_person_text_relation_role',views.add_person_text_relation_role,
		name='add_person_text_relation_role'),
	path('person/add_person_illustration_relation_role',
		views.add_person_illustration_relation_role,
		name='add_person_illustration_relation_role'),
	path('person/add_person_location_relation',views.add_person_location_relation,
		name='add_person_location_relation'),
	path('person/add_person_movement_relation_role',
		views.add_person_movement_relation_role,
		name='add_person_movement_relation_role'),
	path('person/add_person_periodical_relation_role',
		views.add_person_periodical_relation_role,
		name='add_person_periodical_relation_role'),
	path('person/add_movement_type', views.add_movement_type,name='add_movement_type'),
	path('person/add_person_person_relation_type', views.add_person_person_relation_type,
		name='add_person_person_relation_type'),
	path('person/add_pseudonym',views.add_pseudonym,
		name='add_pseudonym'),
]
