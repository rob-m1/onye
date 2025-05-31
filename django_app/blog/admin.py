from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Category, BlogPost, Comment

# Equivalent to calling admin.site.register(User, CustomUserAdmin) later. 
# It tells Django that the CustomUserAdmin class defined below it should be used 
# to manage the User model in the admin interface.
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    pass

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # controls which fields are displayed as columns 
    # on the change list page (the main list view) 
    # for Category objects in the admin
    list_display = ('name', 'description')
    # enables a search box on the change 
    # list page for Category objects
    search_fields = ('name',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    list_filter = ('categories', 'author', 'created_at') 
    # You can filter blog posts by their 'categories', 'author', 'created_at'

    search_fields = ('title', 'content')
    raw_id_fields = ('author',) 
    # For large number of users, use raw_id_fields. Tuple of foreign key or many-to-many fields

    filter_horizontal = ('categories',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author_display', 'name', 'content_snippet', 'created_at')
    # Displays these fields as columns in the comment list view
    
    list_filter = ('post', 'author', 'created_at')
    # Allows filtering comments by post, author, and creation date
    
    search_fields = ('content', 'name')
    # Enables searching within the comment content and name
    
    raw_id_fields = ('post', 'author')
    # Provides a raw ID input for selecting the associated blog post and author

    # Shows either author name or anonymous
    def author_display(self, obj):
        if obj.author:
            return obj.author.username
        return obj.name if obj.name else "Anonymous"
    author_display.short_description = 'Author'

    # Show short part of comment content
    def content_snippet(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_snippet.short_description = 'Content'