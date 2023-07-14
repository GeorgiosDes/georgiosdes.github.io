from django.contrib import admin

from .models import User, Post, Community, Like, Comment

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Community)
admin.site.register(Like)
admin.site.register(Comment)