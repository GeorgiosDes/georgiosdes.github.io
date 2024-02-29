from django.contrib import admin

from .models import User, Game, Guide, New, GuideSection, NewSection, GuideComment, NewComment

# Register your models here.
admin.site.register(User)
admin.site.register(Game)
admin.site.register(Guide)
admin.site.register(New)
admin.site.register(GuideSection)
admin.site.register(NewSection)
admin.site.register(GuideComment)
admin.site.register(NewComment)