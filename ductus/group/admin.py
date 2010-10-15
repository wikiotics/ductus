from django.contrib import admin

from ductus.group.models import Group

class GroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('users',)

admin.site.register(Group, GroupAdmin)
