from django.urls import include,path,re_path

from . import views


app_name = 'persons'
urlpatterns = [
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
	path('person/add_pseudonym',views.add_pseudonym,
		name='add_pseudonym'),
	path('delete/<int:pk>/<str:model_name>', views.delete, name='delete'),
	path('d_movement/<int:pk>',views.detail_movement,
		name='detail_movement'),
	path('d_person/<int:pk>',views.detail_person,
		name='detail_person'),
]

def create_simple_path(name):
	'''creates a simple view based on the model name
	Assumes the form only has a name field.
	'''
	n = views.make_fname(name)
	o = []
	p = "path('add_"+n+"/', views.add_"+n+" , name='add_"+n+"')"
	o.append(eval(p))
	p = "path('add_"+n+"/<int:pk>', views.add_"+n+" , name='add_"+n+"')"
	o.append(eval(p))
	return o

names = 'PersonPersonRelationType,PersonLocationRelationType,PersonTextRelationRole'
names += ',PersonIllustrationRelationRole,PersonMovementRelationRole'
names += ',PersonPeriodicalRelationRole,MovementType,Pseudonym'
for name in names.split(','):
	urlpatterns.extend(create_simple_path(name))

'''
temp = [
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
]
'''
