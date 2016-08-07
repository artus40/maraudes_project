from django.test import TestCase
from .models import Note
# Create your tests here.


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
