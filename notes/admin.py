from django.contrib import admin

from .models import *
# Register your models here.

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):

    fieldsets = [
        ('Contexte',
            {'fields': ['created_by', ('created_date', 'created_time')]
             }
         ),
         ('Note',
          {'fields': ['sujet', 'text']})
    ]

    list_display = ['created_date', 'sujet', 'child_class', 'text']
    list_filter = ('sujet', 'created_date', 'created_by')
