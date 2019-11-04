from django.db import models
from django_countries.fields import CountryField

class Location(models.Model):
	STATUS = [('F','fiction'), ('NF','non-fiction')]
	status = models.CharField(max_length=2,choices=STATUS)
	# location_type = models.ForeignKey(LocationType,on_delete=models.CASCADE)
	country = CountryField()
	city = models.CharField(max_length=100)
	region = models.CharField(max_length=100)
	province = models.CharField(max_length=100)

	def __str__(self):
		return self.status

class LocationType(models.Model):
	pass

class LocationLocationRelation(models.Model):
	pass

class Person(models.Model):
	first_name = models.CharField(max_length=200)
	last_name = models.CharField(max_length=200)
	pseudonyms = models.CharField(max_length=200) #one to many
	GENDER = [('F','female'),('M','male'),('O','other')]
	gender = models.CharField(max_length=1,choices=GENDER)
	date_of_birth = models.DateField()
	date_of_death = models.DateField()
	residence = models.ForeignKey(Location, on_delete=models.CASCADE) # multiple residences?? duplicate of PersonLocationRelation??
	notes = models.TextField() # one to many

class PersonLocationRelation(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	LOCATION_TYPE = [('R','residence'),('T','travel')]
	location_type = models.CharField(max_length=1,choices=LOCATION_TYPE)
	start_date = models.DateField()
	end_date = models.DateField()


class PersonWorkRelationRole(models.Model):
	'''e.g author | illustrator | translator | editor | subject | ... '''
	role = models.CharField(max_length = 100)
	description = models.TextField()


class PersonWorkRelation(models.Model):
	role = models.ForeignKey(PersonWorkRelationRole, on_delete=models.CASCADE)
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
	# unique together [person, role]
	work = '' # FK text | FK illustration
	main_creator = models.BooleanField()
	

class Genre(models.Model):
	name = models.CharField(max_length=100);
	description = models.TextField()

class Text(models.Model):
	title = models.CharField(max_length=300)
	language = models.CharField(max_length=100)
	genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
	upload = models.FileField(upload_to='texts/') # ?


class TextTextRelation(models.Model):
	pass

class Fragment(models.Model):
	pass

class Illustration(models.Model):
	caption =  models.CharField(max_length=300)
	language = models.CharField(max_length=100)
	context = models.TextField()
	illustration_format = '' # ... | ...
	upload = models.ImageField(upload_to='illustrations/') # ?

class IllustrationCategory(models.Model):
	category = models.CharField(max_length=100)
	description = models.TextField()

class IllustrationCategoryRelation(models.Model): # many to many
	illustration = models.ForeignKey(Illustration, on_delete=models.CASCADE)
	category = models.ForeignKey(IllustrationCategory, on_delete=models.CASCADE)




class Periodical(models.Model):
	title = models.CharField(max_length=300)
	language = models.CharField(max_length=100)
	start_date = models.DateField()
	end_date = models.DateField()
	location = models.ForeignKey(Location, on_delete=models.CASCADE)

class Audience(models.Model): # only usefull for periodical not book?
	name = models.CharField(max_length=100)
	description = models.TextField()


class Book(models.Model):
	title = models.CharField(max_length=300) # duplicate -> text
	language = models.CharField(max_length=100) # duplicate -> text
	
class Publisher(models.Model):
	name = models.CharField(max_length=300)
	start_date = models.DateField()
	end_date = models.DateField()
	notes = models.TextField() # many to many

class PublisherLocationRelation(models.Model):
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
	location = models.ForeignKey(Location, on_delete=models.CASCADE)

class PublisherManager(models.Model): #or broker
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
	manager = models.ForeignKey(Person, on_delete=models.CASCADE)


class Publication(models.Model):
	publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
	form = '' # FK periodical | FK book
	issue = models.PositiveIntegerField() # should this be on periodical?
	volume = models.PositiveIntegerField() # should this be on periodical?
	identifier = ''# ISBN
	date = models.DateField()
	location = models.ForeignKey(Location, on_delete=models.CASCADE)
	e_text = models.FileField(upload_to='publication/') # ?

class WorkPublicationRelation(models.Model): #many to many
	work = '' # FK text | FK illustration
	publication = models.ForeignKey(Publication, on_delete=models.CASCADE)












	
