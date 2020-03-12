from django.urls import include,path,re_path

from . import views


app_name = 'catalogue'
urlpatterns = [
	path('',views.TextView.as_view(),name='text_view'),
	path('add_illustration/', views.add_illustration, name='add_illustration'),
	path('add_illustration_category/', views.add_illustration_category, 
		name='add_illustration_category'),
	path('add_text/', views.add_text, name='add_text'),
	path('add_publication/', views.add_publication, name='add_publication'),
	path('add_publisher/', views.add_publisher, name='add_publisher'),
	path('add_publication_type/', views.add_type, name='add_publication_type'),
	path('add_illustration/<str:view>', views.add_illustration, 
		name='add_illustration'),
	path('add_text/<str:view>', views.add_text, name='add_text'),
	path('add_publication/<str:view>', views.add_publication, 
		name='add_publication'),
	path('add_publisher/<str:view>', views.add_publisher, name='add_publisher'),
	path('edit_text/<int:pk>', views.edit_text, name='edit_text'),
	path('edit_publication/<int:pk>', 
		views.edit_publication, name='edit_publication'),
	path('edit_publisher/<int:pk>', views.edit_publisher, name='edit_publisher'),
	path('edit_illustration/<int:pk>', views.edit_illustration, 
		name='edit_illustration'),
	path('text/',views.TextView.as_view(),name='text_list'),
	path('publication/',views.PublicationView.as_view(),name='publication_list'),
	path('publisher/',views.PublisherView.as_view(),name='publisher_list'),
	path('illustration/',views.IllustrationView.as_view(),
		name='illustration_list'),
]
