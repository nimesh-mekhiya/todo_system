from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', )
    list_per_page = 100

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('owner', 'title', 'category', 'due_date', 'status', )
    list_per_page = 100

@admin.register(TodoSharing)
class TodoSharingAdmin(admin.ModelAdmin):
    list_display = ('todo', 'shared_with', 'access_type', 'approval_required', 'approved', )
    list_per_page = 100

@admin.register(TodoChangeLog)
class TodoChangeLogAdmin(admin.ModelAdmin):
    list_display = ('todo', 'user', 'change_description', 'approved_by_owner', )
    list_per_page = 100

@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'todo_sharing', 'activity', 'timestamp', )
    list_per_page = 100