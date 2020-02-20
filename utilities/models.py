from django.db import models
from django.utils import timezone
from utils.model_util import id_generator, info



class Language(models.Model, info):
	name = models.CharField(max_length=100, unique = True)
	iso = models.CharField(max_length=3,null=True,blank=True)

	def __str__(self):
		return self.name
# Create your models here.
