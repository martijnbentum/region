from django.apps import apps

def update_publication_text_illustration():
    update_publication()
    update_text()
    update_illustration()

def update_publication():
    Publication= apps.get_model('catalogue','Publication')
    p = Publication.objects.all()
    print('updating publications, n:',p.count())
    for x in p:
        x._set_publication_location_pks()
        x._set_setting_location_pks()
        x.save()

def update_text():
    Text= apps.get_model('catalogue','Text')
    t = Text.objects.all()
    print('updating texts, n:',t.count())
    for x in t:
        x._set_publication_location_pks()
        x._set_setting_location_pks()
        x._set_publication_years()
        x.save()

def update_illustration():
    Illustration = apps.get_model('catalogue','Illustration')
    i = Illustration.objects.all()
    print('updating illustrations, n:',i.count())
    for x in i:
        x._set_publication_location_pks()
        x._set_setting_location_pks()
        x._set_publication_years()
        x.save()
