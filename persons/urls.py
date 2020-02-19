from django.urls import include,path,re_path

from . import views


app_name = 'persons'
urlpatterns = [
	path('', views.PersonView.as_view(), name='person_list'),
	path('add_person/', views.add_person, name='add_person'),
	path('edit_person/<int:person_id>', views.edit_person, name='edit_person'),
	path('edit_person/<int:person_id>/<str:navbar>/<str:navcontent>', 
		views.edit_person, name='edit_person'),
	path('person/<int:person_id>',views.person_detail,name='person_detail'),
	path('person/add_person_text_relation_role',views.add_person_text_relation_role,
		name='add_person_text_relation_role'),
	path('person/add_person_illustration_relation_role',
		views.add_person_illustration_relation_role,
		name='add_person_illustration_relation_role'),
	path('person/add_person_location_relation',views.add_person_location_relation,
		name='add_person_location_relation'),
]
