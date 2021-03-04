from openpyxl import load_workbook

from catalogue.models import Language, Genre, Text
from persons.models import Person, PersonTextRelation, PersonTextRelationRole

spanish = Language.objects.get(name = 'Spanish')
author = PersonTextRelationRole.objects.get(name = 'author')

class Reader:
	def __init__(self, filename='data/Spanish_texts.xlsx'):
		self.filename = filename
		self.wb = load_workbook(filename)
		self.sheet = self.wb['Main']
		self.column_names = [x for x in list(self.sheet.values)[0] if x != None]
		self.person_translate_dict, self.text_translate_dict = {}, {}


	def get_column(self,name):
		# if name not in column_names: return False
		ci = self.column_names.index(name)
		temp = [x[ci] for x in list(self.sheet.values)[1:]] 
		end_index = 0
		none_found = False
		for i,x in enumerate(temp):
			if x == None and none_found == False: 
				end_index = i
				none_found = True
			if x != None:
				end_index = i +1
				none_found = False
		return temp[:end_index]


	def get_persons(self):
		cn = 'Surname,Name,Gender,Pseudonym,Date of birth,Date of death'.split(',')
		fn = 'last_name,first_name,gender,pseudonym,birth_year,death_year'.split(',')
		temp = []
		for k,o in zip(cn,fn):
			temp.append( self.get_column(k) )
			self.person_translate_dict[k] = o
		self.persons = []
		self.persons_dict = {}
		l = zip(temp[0],temp[1],temp[2],temp[3],temp[4],temp[5])
		for surname, name, gender, pseudonym,birth,death in l:
			p = sPerson(surname,name,gender,pseudonym,birth,death)
			if p not in self.persons:
				self.persons.append(p)
				self.persons_dict[name + ' ' + surname] = p

	def get_genres(self):
		temp =  self.get_column('Type') 
		self.genres= []
		self.genres_dict = {}
		for genre in temp:
			g = sGenre(genre)
			if g not in self.genres:
				self.genres.append(g)
				self.genres_dict[genre] = g
			
	def get_texts(self):
		if not hasattr(self,'persons'):self.get_persons()
		if not hasattr(self,'genres'):self.get_genres()
		temp = []
		cn = 'Title + subtitle,Type,Surname,Name'.split(',')
		fn = 'title,genre,last_name,first_name'.split(',')
		for k,o in zip(cn,fn):
			temp.append( self.get_column(k) )
			self.text_translate_dict[k] = o
		self.texts= []
		self.texts_dict = {}
		self.text_temp = temp
		l = zip(temp[0],temp[1],temp[2],temp[3])
		exclude = 'Prólogo,Callar en vida y perdonar en muerte,Una visita al convento de Santa Inés de Sevilla,La catedral de Sevilla en una tarde de carnaval,Introduction'.split(',')
		self.excluded = []
		for title, genre,surname,name in l:
			if not title or title in exclude: 
				self.excluded.append(title)
				continue
			genre = self.genres_dict[genre]
			person = self.persons_dict[name + ' ' + surname]
			t = sText(title,genre,person)
			if t not in self.texts:
				self.texts.append(t)
				self.texts_dict[title] = t
		
class sPerson:
	def __init__(self,surname,name,gender,pseudonym,birth_year,death_year):
		self.last_name = surname
		self.first_name = name
		self.gender = gender
		self.pseudonym=pseudonym 
		self.birth_year = birth_year
		self.death_year = death_year
		try: 
			self.instance = Person.objects.get(first_name = self.first_name,
				last_name = self.last_name, birth_year = birth_year)
			self.load = True
		except: 
			self.instance = Person(first_name = self.first_name,
				last_name = self.last_name, birth_year = birth_year)
			self.load = False
			self.instance.save()
			

	def __repr__(self):
		m = str(self.first_name) + ' | '+ str(self.last_name) + ' | '+ str(self.gender)
		m += ' | ' + str(self.pseudonym)
		return m

	def __eq__(self,other):
		return self.__dict__ == other.__dict__
		
class sGenre:
	def __init__(self,genre):
		self.genre = genre
		try:
			self.instance = Genre.objects.get(name__iexact = genre)
			self.load = True
		except: 
			self.instance = None
			self.load = False
			
	

	def __repr__(self):
		return str(self.genre)

	def __eq__(self,other):
		return self.__dict__ == other.__dict__
			
			
class sText:
	def __init__(self,title,genre,person):
		self.title = title
		self.genre = genre
		self.person = person
		genre = genre.instance
		person = person.instance
		try: 
			self.instance = Text.objects.get(title = title, language = spanish,genre = genre)
			self.load = True
		except: 
			self.instance = Text(title = title, language = spanish, genre = genre)
			self.load = False
			print(self)
			self.instance.save()
			self.ninstances = 1
		self.make_persontextrelation()

	def make_persontextrelation(self):
		person = self.person.instance
		if self.instance.pk and person.pk:
			try: 
				self.persontextrelation = PersonTextRelation.objects.get(text = self.instance,
					person = person, role= author)
				self.persontextrelation_load = True
			except:
				self.persontextrelation = PersonTextRelation(text = self.instance,
					person = person, role= author)
				self.persontextrelation_load = False
				self.persontextrelation.save()
			


	def __repr__(self):
		return self.title
	
	def __eq__(self,other):
		return self.__dict__ == other.__dict__
		


