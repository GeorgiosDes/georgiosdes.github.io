from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    content_creator = models.BooleanField(default=0)
    

class Game(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='game_images')

    def __str__(self):
        return f"{self.name}"


class Guide(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    title = models.CharField(max_length=55)
    description = models.TextField()
    video_link = models.URLField(max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "title": self.title,
            "description": self.description,
            "video_link": self.video_link,
            "date_created": self.date_created.strftime("%b %d %Y, %I:%M %p"),
        }
    
    def save(self, *args, **kwargs):
        if self.video_link and 'watch?v=' in self.video_link:
            self.video_link = self.video_link.replace('watch?v=', 'embed/')
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        for section in self.guidesection_set.all():
            section.delete()
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user} - {self.title} - {self.game}"
    

class New(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    title = models.CharField(max_length=55)
    description = models.TextField()
    video_link = models.URLField(max_length=250)
    date_created = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "title": self.title,
            "description": self.description,
            "video_link": self.video_link,
            "date_created": self.date_created.strftime("%b %d %Y, %I:%M %p"),
        }
    
    def save(self, *args, **kwargs):
        if self.video_link and 'watch?v=' in self.video_link:
            self.video_link = self.video_link.replace('watch?v=', 'embed/')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        for section in self.newsection_set.all():
            section.delete()
        super().delete(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user} - {self.title} - {self.game}"


class GuideSection(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    content = models.TextField()
    image = models.ImageField(upload_to="guide_images", null=True, blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content
        }

    def __str__(self):
        return f"{self.guide} - {self.title}"
    

class NewSection(models.Model):
    new = models.ForeignKey(New, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    content = models.TextField()
    image = models.ImageField(upload_to="new_images", null=True, blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content
        }
    
    def delete(self, *args, **kwargs):
        if self.image:
            self.image.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.new} - {self.title}"
    

class GuideComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=False)
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.guide.id} - {self.user} said: {self.comment}"
    

class NewComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=False)
    new = models.ForeignKey(New, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "date_created": self.date_created.strftime("%b %d %Y, %I:%M %p")
        }
    
    def __str__(self):
        return f"{self.new.id} - {self.user} said: {self.comment}"