from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        # Fixes pluralization in admin

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts') 
    # many-to-one relationship
    # each BlogPost will have one author
    # and an author can have multiple BlogPosts
    # can get all their blog posts using user.blog_posts.all()
    
    categories = models.ManyToManyField(Category) 
    # many-to-many relationship
    # a BlogPost can belong to multiple Categories
    
    created_at = models.DateTimeField(auto_now_add=True) 
    # sets field's value to current date/time only on instantiation
    
    updated_at = models.DateTimeField(auto_now=True) 
    # updates field's value to current date/time whenever object is saved

    class Meta:
        ordering = ['-created_at'] 
        # Order by creation date, newest first

    def __str__(self):
        return self.title

class Comment(models.Model):
    # Link to the BlogPost
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    # Link to the User if logged in
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='comments')
    # Name needed if no logged in user
    name = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        # Display the author's username else given name
        if self.author:
            return f"Comment by {self.author.username} on {self.post.title}"
        elif self.name:
            return f"Comment by {self.name} on {self.post.title}"
        return f"Anonymous comment on {self.post.title}"