

class info():
	'''inherit from this class to add extra viewing functionality for models'''

	HEADER = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	END = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

	def view(self):
		'''show all attributes of instance'''
		print(self.UNDERLINE,self.__class__,self.END)
		n = max([len(k) for k in self.__dict__.keys()]) + 3
		for k in self.__dict__.keys():
			print(k.ljust(n),self.BLUE,self.__dict__[k], self.END)

class city_info(info):
	def __init__(self,line):
		assert type(line) == list, f'input should be list {line}'
		assert len(line) == 19, f'lenght of line should be 19 {line}'
		self.line = line
		m = 'geonameid,name,asciiname,alternatenames,latitude,longitude'
		m += ',feature_class,feature_code,country_code,cc2,admin1_code'
		m += ',admin2_code,admin3_code,admin4_code,population,elevation'
		m += ',dem,timezone,modification_data'
		self.attribute_names = m.split(',')
		for i,name in enumerate(self.attribute_names):
			setattr(self,name,line[i])

	def set_country(self,country_dict):
		try: self.country = country_dict[self.country_code]
		except: self.country_name='NA'

	def set_continent(self, continent_dict):
		try: self.continent = continent_dict[self.country]
		except: self.continent = 'NA'


class country_info(info):
	'''country information for one country from geonames (see below).'''
	def __init__(self,line):
		'''set information from columns into attributes and create country
		(code, name) tuple.'''
		assert type(line) == list, f'input should be list {line}'
		assert len(line) == 19, f'lenght should be 19 is:{len(line),line}'
		self.line = line
		m = 'iso,iso3,iso_numeric,fips,country,captial,area_km,population'
		m += ',continent,tld,currency_code,currency_name,phone'
		m += ',postal_code_format,postal_code_regex,languages,geonameid'
		m += ',neighbours,equivalentfipscode'
		self.attribute_names = m.split(',')
		for i,name in enumerate(self.attribute_names):
			setattr(self,name,line[i])
		self.code_name = (self.iso,self.country)
		self.continent_code = self.continent
		ccd = code2continent_dict()
		self.continent = ccd[self.continent]

class language_info(info):
	def __init__(self,line):
		assert type(line) == list, 'input should be list'
		assert len(line) == 4, 'lenght of line should be 4'
		self.line = line
		m = 'iso639_3,iso_639_2,iso_639_1,language_name'
		self.attribute_names = m.split(',')
		for i,name in enumerate(self.attribute_names):
			setattr(self,name,line[i])
		self.code_name = (self.iso639_9,self.name)

def country2continent_dict(countries):
	ccd = code2continent_dict()
	output = {} 
	for continent in ccd.values():
		assert continent not in output.keys(), f'{continent} already in {keys}'
		output[continent] = []
		for country in countries:
			name = country.country
			if country.continent == continent: output[continent].append(name)
	return output
	

def code2continent_dict():
	output = {
		'AF':'Africa',
		'AS':'Asia',
		'EU':'Europe',
		'NA':'North America',
		'OC':'Oceania',
		'SA':'South America',
		'AN':'Antartica',
		}
	return output
	

def open_table(f):
	return [line.split('\t') for line in open(f).read().split('\n')]

def make_languages(filename= ''):
	if filename == '':f = 'data/iso-languagecodes.txt' 
	else: f= filename
	languages = open_table(f)
	output = []
	for language in languages:
		if country == ['']: continue
		output.append(language_info(language))
	return output

def make_countries(filename= ''):
	if filename == '':f = 'data/country_codes.txt'
	else: f= filename
	countries = open_table(f)
	output = []
	for country in countries:
		if country == ['']: continue
		output.append(country_info(country))
	return output

def make_country_dict(filename= ''):
	countries = make_countries(filename)
	output = []
	for country in countries:
		output.append(country.code_name)
	return dict(output)
		

def make_cities(filename=''):
	if filename == '': f = 'data/cities500.txt'
	cities = open_table(f)
	countries = make_country_dict()
	country2continent = country2continent_dict()
	output = []
	for city in cities:
		if city == ['']: continue
		output.append(city_info(city))
		output[-1].set_country(countries)
		output[-1].set_continent(country2continent)
	return output

	

'''
city_info attribute name legend
https://download.geonames.org/export/dump/
The main 'geoname' table has the following fields :
---------------------------------------------------
geonameid         : integer id of record in geonames database
name              : name of geographical point (utf8) varchar(200)
asciiname         : name of geographical point in plain ascii characters, varchar(200)
alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
latitude          : latitude in decimal degrees (wgs84)
longitude         : longitude in decimal degrees (wgs84)
feature class     : see http://www.geonames.org/export/codes.html, char(1)
feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
country code      : ISO-3166 2-letter country code, 2 characters
cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80) 
admin3 code       : code for third level administrative division, varchar(20)
admin4 code       : code for fourth level administrative division, varchar(20)
population        : bigint (8 byte int) 
elevation         : in meters, integer
dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
modification date : date of last modification in yyyy-MM-dd format
'''
