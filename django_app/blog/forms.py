from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, BlogPost, Category, Comment

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class UserLoginForm(AuthenticationForm):
    # AuthenticationForm handles username and password
    pass

class BlogPostForm(forms.ModelForm):
    # Text input of categories
    # Holds comma-separated category names
    category_names = forms.CharField(
        label='Categories (comma-separated)',
        required=False,
        help_text='Enter category names, separated by commas. New categories will be created automatically.'
    )

    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'category_names']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['category_names'] = ", ".join([cat.name for cat in self.instance.categories.all()])

    def clean_category_names(self):
        # Clean and process the category names
        category_names_str = self.cleaned_data['category_names']
        category_names_list = [name.strip() for name in category_names_str.split(',') if name.strip()]
        return category_names_list

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save() 
            # Save BlogPost instance to get ID
            
            self.save_m2m()
            # Save ManyToMany relationships

        # Handle category creation and assignment
        category_names = self.cleaned_data.get('category_names', [])
        categories_to_assign = []
        for cat_name in category_names:
            category, created = Category.objects.get_or_create(name=cat_name)
            categories_to_assign.append(category)

        instance.categories.set(categories_to_assign)
        # Set new categories

        return instance

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'content']

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.request and self.request.user.is_authenticated:
            # Logged in, name not needed
            self.fields['name'].required = False
            self.fields['name'].widget = forms.HiddenInput() # Hide the name field
        else:
            # If anonymous user
            self.fields['name'].required = True
            self.fields['name'].label = "Your Name"

