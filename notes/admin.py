from django.contrib import admin

from .models import *
# Register your models here.

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):

    list_display = ['created_date', 'sujet']
    list_filter = ('sujet', 'created_date', 'created_by')
