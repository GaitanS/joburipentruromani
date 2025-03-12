from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.conf import settings

from .models import BlogPost, BlogCategory, BlogTag, BlogComment

class BlogHomeView(ListView):
    """Blog homepage view showing featured and recent posts"""
    model = BlogPost
    template_name = 'blog/blog_home.html'
    context_object_name = 'posts'
    paginate_by = settings.BLOG_POSTS_PER_PAGE

    def get_queryset(self):
        """Return published blog posts ordered by published date"""
        return BlogPost.objects.filter(
            status='published', 
            published_at__lte=timezone.now()
        ).order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured posts for carousel
        context['featured_posts'] = BlogPost.objects.filter(
            status='published',
            featured=True,
            published_at__lte=timezone.now()
        ).order_by('-published_at')[:5]
        
        # Categories for sidebar
        context['categories'] = BlogCategory.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status='published', posts__published_at__lte=timezone.now()))
        ).filter(post_count__gt=0).order_by('-post_count')
        
        # Popular tags
        context['popular_tags'] = BlogTag.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status='published', posts__published_at__lte=timezone.now()))
        ).filter(post_count__gt=0).order_by('-post_count')[:15]
        
        # SEO metadata
        context['meta_title'] = 'Blog - JoburiPentruRomani'
        context['meta_description'] = 'Articole despre carieră, sfaturi pentru căutarea unui loc de muncă și ghiduri pentru profesioniști.'
        
        return context

class BlogCategoryView(ListView):
    """View for listing posts in a specific category"""
    model = BlogPost
    template_name = 'blog/blog_category.html'
    context_object_name = 'posts'
    paginate_by = settings.BLOG_POSTS_PER_PAGE
    
    def get_queryset(self):
        self.category = get_object_or_404(BlogCategory, slug=self.kwargs['slug'])
        return BlogPost.objects.filter(
            category=self.category,
            status='published',
            published_at__lte=timezone.now()
        ).order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        
        # SEO metadata
        if self.category.meta_title:
            context['meta_title'] = self.category.meta_title
        else:
            context['meta_title'] = f'Articole despre {self.category.name} - JoburiPentruRomani Blog'
            
        if self.category.meta_description:
            context['meta_description'] = self.category.meta_description
        else:
            context['meta_description'] = f'Descoperă cele mai recente articole despre {self.category.name} pe JoburiPentruRomani. Sfaturi pentru carieră și informații utile.'
        
        return context

class BlogTagView(ListView):
    """View for listing posts with a specific tag"""
    model = BlogPost
    template_name = 'blog/blog_tag.html'
    context_object_name = 'posts'
    paginate_by = settings.BLOG_POSTS_PER_PAGE
    
    def get_queryset(self):
        self.tag = get_object_or_404(BlogTag, slug=self.kwargs['slug'])
        return BlogPost.objects.filter(
            tags=self.tag,
            status='published',
            published_at__lte=timezone.now()
        ).order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        
        # SEO metadata
        context['meta_title'] = f'Articole despre #{self.tag.name} - JoburiPentruRomani Blog'
        context['meta_description'] = f'Articole și sfaturi despre #{self.tag.name}. Informații utile pentru cariera ta.'
        
        return context

class BlogDetailView(DetailView):
    """View for displaying a single blog post"""
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    
    def get_object(self, queryset=None):
        post = super().get_object(queryset=queryset)
        
        # Check if post is published or if user has staff privileges
        if post.status != 'published' and not self.request.user.is_staff:
            raise Http404("Acest articol nu este disponibil.")
        
        # Check if publish date has passed or if user has staff privileges
        if post.published_at > timezone.now() and not self.request.user.is_staff:
            raise Http404("Acest articol nu este disponibil.")
            
        return post
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        
        # Related posts by category, excluding current post
        context['related_posts'] = BlogPost.objects.filter(
            category=post.category,
            status='published',
            published_at__lte=timezone.now()
        ).exclude(id=post.id).order_by('-published_at')[:3]
        
        # Comments
        context['comments'] = post.comments.filter(approved=True).order_by('-created_at')
        
        # SEO metadata
        if post.meta_title:
            context['meta_title'] = post.meta_title
        else:
            context['meta_title'] = post.title
            
        if post.meta_description:
            context['meta_description'] = post.meta_description
            
        context['meta_keywords'] = post.meta_keywords
        
        return context
        
    def post(self, request, *args, **kwargs):
        """Handle comment submission"""
        post = self.get_object()
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        website = request.POST.get('website', '')
        content = request.POST.get('content')
        
        if name and email and content:
            # Auto-approve comments from staff
            approved = request.user.is_staff
            
            BlogComment.objects.create(
                post=post,
                name=name,
                email=email,
                website=website,
                content=content,
                approved=approved
            )
            
            if approved:
                messages.success(request, "Comentariul tău a fost adăugat.")
            else:
                messages.info(request, "Comentariul tău a fost trimis și este în așteptare pentru aprobare.")
        else:
            messages.error(request, "Te rugăm să completezi toate câmpurile obligatorii.")
            
        return redirect('jobs:blog_detail', slug=post.slug)

class BlogSearchView(ListView):
    """View for blog search results"""
    model = BlogPost
    template_name = 'blog/blog_search.html'
    context_object_name = 'posts'
    paginate_by = settings.BLOG_POSTS_PER_PAGE
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return BlogPost.objects.filter(
                Q(title__icontains=query) | 
                Q(summary__icontains=query) | 
                Q(content__icontains=query),
                status='published',
                published_at__lte=timezone.now()
            ).order_by('-published_at')
        return BlogPost.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        context['query'] = query
        
        # SEO metadata
        context['meta_title'] = f'Rezultate căutare: {query} - JoburiPentruRomani Blog'
        context['meta_description'] = f'Articole și sfaturi despre {query}. Informații utile pentru cariera ta.'
        
        return context

# Admin Views for Blog Management (staff only)
class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff status for blog management views"""
    def test_func(self):
        return self.request.user.is_staff

class BlogAdminListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Admin view for listing all blog posts"""
    model = BlogPost
    template_name = 'blog/admin/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 20
    
    def get_queryset(self):
        return BlogPost.objects.all().order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Administrare Blog'
        return context

class BlogAdminCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """Admin view for creating a new blog post"""
    model = BlogPost
    template_name = 'blog/admin/blog_edit.html'
    fields = ['title', 'category', 'tags', 'summary', 'content', 'featured_image', 
              'meta_title', 'meta_description', 'meta_keywords', 'status', 
              'featured', 'published_at', 'enable_comments']
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Articol nou'
        context['submit_text'] = 'Crează'
        return context

class BlogAdminUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """Admin view for updating an existing blog post"""
    model = BlogPost
    template_name = 'blog/admin/blog_edit.html'
    fields = ['title', 'category', 'tags', 'summary', 'content', 'featured_image', 
              'meta_title', 'meta_description', 'meta_keywords', 'status', 
              'featured', 'published_at', 'enable_comments']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editează articol'
        context['submit_text'] = 'Actualizează'
        return context

class BlogAdminDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """Admin view for deleting a blog post"""
    model = BlogPost
    template_name = 'blog/admin/blog_delete.html'
    success_url = reverse_lazy('jobs:blog_admin')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Șterge articol'
        return context

class BlogCommentAdminView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Admin view for managing comments"""
    model = BlogComment
    template_name = 'blog/admin/comment_list.html'
    context_object_name = 'comments'
    paginate_by = 30
    
    def get_queryset(self):
        return BlogComment.objects.all().order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Administrare Comentarii'
        context['pending_count'] = BlogComment.objects.filter(approved=False).count()
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle comment approval/rejection via AJAX"""
        if request.is_ajax():
            comment_id = request.POST.get('comment_id')
            action = request.POST.get('action')
            
            try:
                comment = BlogComment.objects.get(id=comment_id)
                
                if action == 'approve':
                    comment.approved = True
                    comment.save()
                    return JsonResponse({'status': 'success', 'message': 'Comentariu aprobat'})
                elif action == 'reject':
                    comment.delete()
                    return JsonResponse({'status': 'success', 'message': 'Comentariu șters'})
                    
                return JsonResponse({'status': 'error', 'message': 'Acțiune nevalidă'})
            except BlogComment.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Comentariu negăsit'})
                
        return redirect('jobs:blog_comments_admin')