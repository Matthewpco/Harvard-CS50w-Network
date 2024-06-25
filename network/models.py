from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Post(models.Model):
    content = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")

    def __str__(self):
        return f"Post {self.id} by {self.author} on {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

class Followers(models.Model):
    follows = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follows")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")

    def __str__(self):
        return f"{self.follows} {self.following}"
    
class Likes(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="liked_by")

    def __str__(self):
        return f"{self.author} {self.post}"
