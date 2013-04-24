from codewiki.models import Code, View, Scraper, UserCodeRole, ScraperRunEvent, CodePermission
from django.contrib.auth.models import User
from django.contrib import admin
from django.db import models
from django.db.models import Count
from django import forms
# from django.contrib.admin import SimpleListFilter

class UserCodeRoleInlines(admin.TabularInline):
    model = UserCodeRole
    extra = 1

def mark_featured(modeladmin, request, queryset):
    queryset.update(featured=True)
mark_featured.short_description = 'Mark selected items as featured'

def mark_unfeatured(modeladmin, request, queryset):
    queryset.update(featured=False)
mark_unfeatured.short_description = 'Mark selected items as unfeatured'

class CodeAdmin(admin.ModelAdmin):
    inlines = (UserCodeRoleInlines,)
    readonly_fields = ('wiki_type','guid')
    list_display = ('title', 'short_name', 'owner_name', 'status', 'privacy_status')
    list_filter = ('status', 'privacy_status', 'featured', 'created_at')
    search_fields = ('title', 'short_name')

    def owner_name(self, obj):
        if obj.owner():
            return obj.owner().username
        return None

class ScraperAdmin(CodeAdmin):
    actions = [mark_featured, mark_unfeatured]

class ViewAdmin(CodeAdmin):
    actions = [mark_featured, mark_unfeatured]


class ScraperRunEventAdmin(admin.ModelAdmin):
    list_display = ('run_id', 'scraper', 'run_started', 'run_ended', 'pages_scraped', 'first_url_scraped')
    search_fields = ('first_url_scraped',)

admin.site.register(Scraper, ScraperAdmin)
admin.site.register(View, ViewAdmin)
admin.site.register(ScraperRunEvent, ScraperRunEventAdmin)
admin.site.register(CodePermission)




