# admin interface -- for debugging only

from django.contrib import admin

from ductus.wiki.models import WikiPage, WikiRevision

class WikiPageAdmin(admin.ModelAdmin):
    pass

class WikiRevisionAdmin(admin.ModelAdmin):
    pass

admin.site.register(WikiPage, WikiPageAdmin)
admin.site.register(WikiRevision, WikiRevisionAdmin)
