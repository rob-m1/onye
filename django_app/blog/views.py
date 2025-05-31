from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, ListView
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q
from .models import BlogPost, Category, User, Comment
from .forms import UserRegisterForm, UserLoginForm, CategoryForm, CommentForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

class PostListView(ListView):
    model = BlogPost
    template_name = 'blog/home.html'
    context_object_name = 'blog_posts'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtering by category
        category_name = self.request.GET.get('category')
        if category_name:
            queryset = queryset.filter(categories__name=category_name)

        # Search by title/content
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))

        # Query optimization as described in the instructions
        queryset = queryset.select_related('author').prefetch_related('categories')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('q', '')
        selected_category_obj = None
        if context['current_category']:
            try:
                selected_category_obj = Category.objects.get(name=context['current_category'])
            except Category.DoesNotExist:
                selected_category_obj = None
        context['selected_category_obj'] = selected_category_obj
        return context
    
    def get_template_names(self):
        # This is the preferred HTMX handling for template switching
        if self.request.headers.get('HX-Request'):
            return ['blog/includes/post_list.html']
        return [self.template_name]

class PostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        # Query optimization as described in the instructions
        return super().get_queryset().select_related('author').prefetch_related('categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm(request=self.request)
        context['comments'] = self.object.comments.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object() 
        
        form = CommentForm(request.POST, request=request)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            if request.user.is_authenticated:
                comment.author = request.user
                comment.name = request.user.username

            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('blog:post_detail', pk=self.object.pk)
        else:
            context = self.get_context_data(**kwargs)
            context['comment_form'] = form 
            
            return self.render_to_response(context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # password hashed automatically before being saved in the database

            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('blog:home')
    else:
        form = UserRegisterForm()
    return render(request, 'blog/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            # verifies the provided password against the stored hashed password without exposing the plain-text password
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('blog:home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'blog/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('blog:home')

class PostCreateView(LoginRequiredMixin, CreateView):
    model = BlogPost
    fields = ['title', 'content', 'categories'] # <--- Ensure 'categories' is in this list
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BlogPost
    fields = ['title', 'content', 'categories']
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('blog:home')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BlogPost
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('blog:home')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

@login_required
def create_category_htmx(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            return JsonResponse({
                'id': category.id,
                'name': category.name,
                'success': True
            })
        else:
            html = render_to_string('blog/includes/category_form_modal.html', {'category_form': form}, request=request)
            return JsonResponse({'html': html, 'success': False})
    else:
        form = CategoryForm()
        html = render_to_string('blog/includes/category_form_modal.html', {'category_form': form}, request=request)
        return JsonResponse({'html': html, 'success': True})

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
            form.instance.name = self.request.user.username
        return super().form_valid(form)

    def test_func(self):
        comment = self.get_object()
        if self.request.user.is_authenticated:
            return self.request.user == comment.author
        else:
            if not comment.author and comment.name:
                return False
            return False

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.post.pk})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'

    def test_func(self):
        comment = self.get_object()
        if self.request.user.is_authenticated:
            return self.request.user == comment.author
        else:
            return False

    def get_success_url(self):
        post_pk = self.get_object().post.pk
        messages.success(self.request, "Comment deleted successfully!")
        return reverse_lazy('blog:post_detail', kwargs={'pk': post_pk})