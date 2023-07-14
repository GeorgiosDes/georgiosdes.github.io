from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    username = models.CharField(max_length=64,blank=True)
    content = models.CharField(max_length=1000)
    likes = models.IntegerField(default=0)
    comments = models.CharField(max_length=1000,blank=True)
    edited = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "username": self.username,
            "content": self.content,
            "likes": self.likes,
            "comments": self.comments,
            "edited": self.edited,
            "date_created": self.date_created.strftime("%b %d %Y, %I:%M %p"),
        }
    
    def __str__(self):
        return f"{self.username} - {self.content}"
    

class Community(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="community")
    following = models.ManyToManyField(User, related_name="following")
    followers = models.ManyToManyField(User, related_name="followers")

    def __str__(self):
        following_list = self.following.all()
        following_users = ', '.join([str(user) for user in following_list])
        followers_list = self.followers.all()
        followers_users = ', '.join([str(user) for user in followers_list])
        return f"{self.user} | Following: {following_users} | Followers: {followers_users}"
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_liked")
    post = models.ManyToManyField(Post, related_name="post_liked")

    def __str__(self):
        post_list = self.post.values_list("id", flat=True)
        posts = ', '.join([str(post) for post in post_list])
        return f"{self.user} liked: {posts}"
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.post.id} - {self.user} said: {self.comment}"