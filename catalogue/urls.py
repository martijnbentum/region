from django.urls import include,path,re_path

from . import views


app_name = 'catalogue'
urlpatterns = [
	path('',views.TextView.as_view(),name='text_view'),
	path('add_text/', views.add_text, name='add_text'),
	path('add_publication/', views.add_publication, name='add_publication'),
	path('add_publisher/', views.add_publisher, name='add_publisher'),
	path('add_binding/', views.add_publisher, name='add_binding'),
	path('edit_text/<int:pk>', views.edit_text, name='edit_text'),
	path('edit_publication/<int:pk>', 
		views.edit_publication, name='edit_publication'),
	path('edit_publisher/<int:pk>', views.edit_publisher, name='edit_publisher'),
	path('text/',views.TextView.as_view(),name='text_list'),
	path('publication/',views.PublicationView.as_view(),name='publication_list'),
	path('publisher/',views.PublisherView.as_view(),name='publisher_list'),
]
