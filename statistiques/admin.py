from django.contrib import admin
from .models import GroupeLieux
# Register your models here.

@admin.register(GroupeLieux)
class GroupLieuxAdmin(admin.ModelAdmin):
    model = GroupeLieux
    filter_horizontal = ["lieux"]