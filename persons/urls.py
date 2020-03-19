from django.urls import include,path,re_path

from . import views


app_name = 'persons'
urlpatterns = [
	path('', views.PersonView.as_view(), name='person_list'),
	path('literary_movement_list', views.LiteraryMovementView.as_view(), 
		name='literary_movement_list'),
	path('add_person/', views.edit_person, name='add_person'),
	path('add_person/<str:view>', views.edit_person, name='add_person'),
	path('add_literary_movement/', views.edit_literary_movement, name='add_literary_movement'),
	path('add_literary_movement/<str:view>', views.edit_literary_movement, 
		name='add_literary_movement'),
	path('edit_person/<int:person_id>', views.edit_person, name='edit_person'),
	path('edit_person/<int:person_id>/<str:focus>', 
		views.edit_person, name='edit_person'),
	path('edit_literary_movement/<int:pk>', views.edit_literary_movement, 
		name='edit_literary_movement'),
	path('edit_literary_movement/<int:pk>/<str:focus>', views.edit_literary_movement, 
		name='edit_literary_movement'),
	path('person/<int:person_id>',views.person_detail,name='person_detail'),
	path('person/add_person_text_relation_role',views.add_person_text_relation_role,
		name='add_person_text_relation_role'),
	path('person/add_person_illustration_relation_role',
		views.add_person_illustration_relation_role,
		name='add_person_illustration_relation_role'),
	path('person/add_person_location_relation',views.add_person_location_relation,
		name='add_person_location_relation'),
	path('person/add_person_literary_movement_relation_role',
		views.add_person_literary_movement_relation_role,
		name='add_person_literary_movement_relation_role'),
	path('person/add_pseudonym',views.add_pseudonym,
		name='add_pseudonym'),
]
