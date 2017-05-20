from django.core.exceptions import ValidationError
from django.test import TestCase
from .models import Note, Sujet
# Create your tests here.

# TODO: test 'actions.py'


class SujetModelTestCase(TestCase):

    def setUp(self):
        pass

    def test_statistiques_is_autocreated(self):
        new_sujet = Sujet.objects.create(prenom="Astérix")
        self.assertIsNotNone(new_sujet.statistiques)

    def test_at_least_one_in_name_surname_firstname(self):
        self.assertIsInstance(Sujet.objects.create(nom="DeGaulle"), Sujet)
        self.assertIsInstance(Sujet.objects.create(surnom="Le Gaulois"), Sujet)
        self.assertIsInstance(Sujet.objects.create(prenom="Astérix"), Sujet)

    def test_raises_validation_error_if_no_name(self):
        with self.assertRaises(ValidationError):
            Sujet.objects.create(age=25)

class NoteManagerTestCase(TestCase):
    """ managers.NoteManager Test Case """

    def setUp(self):
        from notes.managers import NoteManager
        self.note_manager = NoteManager

    def test_note_default_manager_is_NoteManager(self):
        self.assertIsInstance(Note.objects, self.note_manager,
            msg="%s is not Note default manager" % self.note_manager)

    def test_by_date(self):
        prev_note = None
        for note in Note.objects.by_date(reverse=False):
            if not prev_note:
                prev_note = note
            else:
                self.assertLessEqual(prev_note.created_date, note.created_date,
                            msg="%s is not same date or prior to %s" % (prev_note, note))
                prev_note = note

    def test_by_date_reversed(self):
        prev_note = None
        for note in Note.objects.by_date(reverse=True):
            if not prev_note:
                prev_note = note
            else:
                self.assertGreaterEqual(prev_note.created_date, note.created_date,
                            msg="%s is not same date or later to %s" % (prev_note, note))
                prev_note = note

    def test_by_time(self):
        prev_note = None
        for note in Note.objects.by_time(reverse=False):
            if not prev_note:
                prev_note = note
            else:
                self.assertLessEqual(prev_note.created_time, note.created_time,
                            msg="%s is not same time or prior to %s" % (prev_note, note))
                prev_note = note

    def test_by_time_reversed(self):
        prev_note = None
        for note in Note.objects.by_time(reverse=True):
            if not prev_note:
                prev_note = note
            else:
                self.assertLessEqual(prev_note.created_time, note.created_time,
                            msg="%s is not same time or later to %s" % (prev_note, note))
                prev_note = note

class NoteQuerySetTestCase(TestCase):

    def setUp(self):
        self.qs = Note.objects.all()

    def test_by_date(self):
        prev_note = None
        for note in self.qs.by_date(reverse=False):
            if not prev_note:
                prev_note = note
            else:
                self.assertLessEqual(prev_note.created_date, note.created_date,
                            msg="%s is not same date or prior to %s" % (prev_note, note))
                prev_note = note

    def test_by_date_reversed(self):
        prev_note = None
        for note in self.qs.by_date(reverse=True):
            if not prev_note:
                prev_note = note
            else:
                self.assertGreaterEqual(prev_note.created_date, note.created_date,
                            msg="%s is not same date or later to %s" % (prev_note, note))
                prev_note = note

    def test_by_time(self):
        prev_note = None
        for note in self.qs.by_time(reverse=False):
            if not prev_note:
                prev_note = note
            else:
                self.assertLessEqual(prev_note.created_time, note.created_time,
                            msg="%s is not same time or prior to %s" % (prev_note, note))
                prev_note = note

    def test_by_time_reversed(self):
        prev_note = None
        for note in self.qs.by_time(reverse=True):
            if not prev_note:
                prev_note = note
            else:
                self.assertLessEqual(prev_note.created_time, note.created_time,
                            msg="%s is not same time or later to %s" % (prev_note, note))
                prev_note = note
