import datetime
import csv

def parse_rows(data_file):

    reader = csv.DictReader(data_file, delimiter=";")

    for i, row in enumerate(reader):
        date = datetime.datetime.strptime(row['DATE'] + ".2016", "%d.%m.%Y").date()
        lieu = row['LIEUX']
        nom, prenom = row['NOM'], row['PRENOM']
        prem_rencontre = True if row['1 ER CONTACT'].lower() == "oui" else False

        yield i, date, lieu, nom, prenom, prem_rencontre

from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):

    help = "Load data for rencontre from csv files"

    def add_arguments(self, parser):
        parser.add_argument('file', help="path to the files to load", nargs="+", type=str)
        parser.add_argument('--commit', help="commit changes to the database", 
                            action="store_true", dest="commit", default=False)
        parser.add_argument('--check', action='store_true', dest='check', default=False,
                            help="Check that all lines from file are written into database")

    @property
    def cache(self):
        if not hasattr(self, '_cache'):
            self._cache = {'maraude': {}, 'lieu': {}, 'sujet': {}, 'rencontre': [], 'observation': []}
        return self._cache

    def new_object(self, model, data, cache_key=None):
        """ Create new object, add it to cache (in dict if cache_key is given, in list otherwise).
            Save it only if --commit option is given 
        """
        obj = model(**data)
        msg = "[%i]+ Created %s " % (self.cur_line, obj)
        if self._commit:
            obj.save()
            msg += " successfully saved to db"
        if cache_key:
            self.cache[model.__qualname__.lower()][cache_key] = obj
            msg += " and added to cache."
        self.stdout.write(self.style.SUCCESS(msg))
        return obj

    @property
    def referent_maraude(self):
        if not hasattr(self, '_referent'):
            from utilisateurs.models import Maraudeur
            self._referent = Maraudeur.objects.get_referent()
        return self._referent

    def find_maraude(self, date):
        from maraudes.models import Maraude
        try: # First, try to retrieve from database
            obj = Maraude.objects.get(date=date)
        except Maraude.DoesNotExist:
            # Try to retrieve from cache
            try:
                obj = self.cache['maraude'][date]
            except KeyError:
                # Create a new object and put it into cache
                obj = self.new_object(
                    Maraude,
                    {'date':date, 'referent':self.referent_maraude, 'binome':self.referent_maraude}, 
                    cache_key=date)
        return obj

    def find_sujet(self, nom, prenom):
        from sujets.models import Sujet
        from watson import search

        search_text = "%s %s" % (nom, prenom)
        sujet = self.cache['sujet'].get(search_text, None)

        while not sujet:
            create = False #Set to True if creation is needed at and of loop
            self.stdout.write(self.style.WARNING("In line %i, searching : %s. " % (self.cur_line, search_text)), ending='')
            results = search.filter(Sujet, search_text)

            if results.count() == 1: # Always ask to review result a first time
                sujet = results[0]
                self.stdout.write(self.style.SUCCESS("Found %s '%s' %s" % (sujet.nom, sujet.surnom, sujet.prenom)))
                action = input("Confirm ? (y/n/type new search)> ")
                if action == "n":
                    sujet = None
                    search_text = "%s %s" % (nom, prenom)
                elif action == "y":
                    continue
                else: # In case the result is no good at all !
                    sujet = None
                    search_text = action

            elif results.count() > 1: # Ask to find the appropriate result
                self.stdout.write(self.style.WARNING("Multiple results for %s" % search_text))
                for i, result in enumerate(results):
                    self.stdout.write("%i. %s '%s' %s" % (i, result.nom, result.surnom, result.prenom))
                choice = input("Choose the right number - Type new search - C to create '%s %s': " % (nom, prenom))
                if choice == "C":
                    create = True
                else:
                    try: sujet = results[int(choice)]
                    except (IndexError, ValueError): 
                        search_text = str(choice) #New search
                        continue

            else: # No results, try with name only, or ask for new search
                if search_text == "%s %s" % (nom, prenom):
                    # Search only with nom
                    self.stdout.write(self.style.WARNING("Nothing, trying name only..."), ending='')
                    search_text = nom if nom else prenom
                    continue
                else:
                    self.stdout.write(self.style.ERROR("No result !"))
                    action = input("New search or C to create '%s %s': " % (nom, prenom))
                    if action == "C":
                        create = True
                    else:
                        search_text = str(action)

            if create:
                sujet = self.new_object(
                            Sujet,
                            {'nom':nom, 'prenom':prenom}
                            )
                self.stdout.write('Created, %s' % sujet)
        # Always store sujet in cache because it may or may not be updated, safer to save in all cases.
        self.cache['sujet']["%s %s" % (nom, prenom)] = sujet
        return sujet

    def find_lieu(self, nom):
        from maraudes.models import Lieu

        try:
            lieu = Lieu.objects.get(nom=nom)
        except Lieu.DoesNotExist:
            lieu = self.cache['lieu'].get(nom, None)
            while not lieu:
                self.stdout.write(self.style.WARNING("At line %i, le lieu '%s' n'a pas été trouvé" % (self.cur_line, nom)))
                action = input('%s (Créer/Sélectionner)> ' % nom)
                if action == "C":
                    lieu = self.new_object(Lieu, {'nom': nom}, cache_key=nom)
                elif action == "S":
                    choices = {l.pk:l.nom for l in Lieu.objects.all()}
                    for key, name in choices.items():
                        self.stdout.write("%i. %s" % (key, name))
                    while not lieu:
                        chosen_key = input('Choose a number: ')
                        try:
                            lieu = Lieu.objects.get(pk=chosen_key)
                            confirm = input("Associer %s à %s ? (o/n)> " % (nom, lieu.nom))
                            if confirm == "n":
                                lieu = None
                            else:
                                self.cache['lieu'][nom] = lieu

                        except (Lieu.DoesNotExist, ValueError):
                            lieu = None
                else:
                    continue

        return lieu

    def add_rencontre(self, maraude, sujet, lieu):
        from maraudes.models import Rencontre
        from maraudes.notes import Observation

        rencontre = self.new_object(Rencontre,
                                    {'maraude':maraude, 'lieu':lieu, 'heure_debut':datetime.time(20, 0),
                              'duree':15})
        observation = self.new_object(Observation, {'rencontre':rencontre, 
                                                    'sujet':sujet, 
                                                    'text':"Chargé depuis '%s'" % self._file.name})
        self.cache['rencontre'].append(rencontre)
        self.cache['observation'].append(observation)

    def handle(self, **options):
        """ Parsing all given files, look for existing objects and create new Rencontre
            and Observation objects. Ask for help finding related object, creating new ones
            if needed. All creation/updates are stored in cache and commited only after
            user confirmation 
        """

        self._commit = options.get('commit', False)

        for file_path in options['file']:
            with open(file_path, 'r') as data_file:
                self.stdout.write("Working with '%s'" % data_file.name)
                self._file = data_file
                for line, date, lieu, nom, prenom, prems in parse_rows(data_file):
                    self.cur_line = line
                    maraude = self.find_maraude(date)
                    lieu = self.find_lieu(lieu)
                    sujet = self.find_sujet(nom, prenom)
                    assert sujet is not None
                    assert lieu is not None
                    assert maraude is not None
                    self.add_rencontre(maraude, sujet, lieu)

                #Summary
                self.stdout.write(" ## %s : %i lines ##" % (data_file.name, self.cur_line))
                self.stdout.write("Trouvé %s nouvelles observations" % len(self.cache['observation']))
                self.stdout.write("Nécessite l'ajout/modification de : \n- %i maraudes\n- %i lieux\n- %i sujets" %
                                  (len(self.cache['maraude']), len(self.cache['lieu']), len(self.cache['sujet'])))

                view = input('Voulez-vous voir la liste des changements ? (o/n)> ')
                if view == "o": self.stdout.write(" ## Changements ## \n%s" % self.cache)
