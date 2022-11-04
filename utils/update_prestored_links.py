from django.apps import apps

def update_all():
    update_publication()
    update_text()
    update_illustration()
    update_person()
    update_movement()
    update_periodical()
    update_publisher()
        
    

def update_publication():
    Publication= apps.get_model('catalogue','Publication')
    p = Publication.objects.all()
    print('updating publications, n:',p.count())
    for x in p:
        x._set_publication_location_pks()
        x._set_setting_location_pks()
        x._set_connection_count()
        x._set_form_name()
        x._set_language_names()

def update_text():
    Text= apps.get_model('catalogue','Text')
    t = Text.objects.all()
    print('updating texts, n:',t.count())
    for x in t:
        x._set_publication_location_pks()
        x._set_setting_location_pks()
        x._set_publication_years()
        x._set_connection_count()
        x._set_language_name()

def update_illustration():
    Illustration = apps.get_model('catalogue','Illustration')
    i = Illustration.objects.all()
    print('updating illustrations, n:',i.count())
    for x in i:
        x._set_publication_location_pks()
        x._set_setting_location_pks()
        x._set_publication_years()
        x._set_connection_count()

def update_person():
    Person= apps.get_model('persons','Person')
    p = Person.objects.all()
    print('updating persons, n:',p.count())
    for x in p:
        x._set_connection_count()

def update_movement():
    Movement= apps.get_model('persons','Movement')
    m = Movement.objects.all()
    print('updating movements, n:',m.count())
    for x in m:
        x._set_connection_count()

def update_periodical():
    Periodical= apps.get_model('catalogue','Periodical')
    p = Periodical.objects.all()
    print('updating periodicals, n:',p.count())
    for x in p:
        x._set_connection_count()

def update_publisher():
    Publisher= apps.get_model('catalogue','Publisher')
    p = Publisher.objects.all()
    print('updating publisher, n:',p.count())
    for x in p:
        x._set_connection_count()
    
