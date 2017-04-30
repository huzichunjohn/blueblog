from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect, HttpResponseForbidden
from django.utils.text  import slugify
from django.views.generic import CreateView, TemplateView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from blog.forms import BlogForm, BlogPostForm
from blog.models import Blog, BlogPost

class NewBlogView(CreateView):
    form_class = BlogForm
    template_name = 'blog_settings.html'

    def form_valid(self, form):
        blog_obj = form.save(commit=False)
        blog_obj.owner = self.request.user
        blog_obj.slug = slugify(blog_obj.title)

        blog_obj.save()
        return HttpResponseRedirect(reverse('home'))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if Blog.objects.filter(owner=user).exists():
            return HttpResponseForbidden('You can not create more than one blogs per account')
        else:
            return super(NewBlogView, self).dispatch(request, *args, **kwargs)

class Homeview(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super(Homeview, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            if Blog.objects.filter(owner=self.request.user).exists():
                ctx['has_blog'] = True
                blog = Blog.objects.get(owner=self.request.user)

                ctx['blog'] = blog
                ctx['blog_posts'] = BlogPost.objects.filter(blog=blog)

        return ctx

class UpdateBlogView(UpdateView):
    form_class = BlogForm
    template_name = 'blog_settings.html'
    success_url = '/'
    model = Blog

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateBlogView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(UpdateBlogView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            if Blog.objects.filter(owner=self.request.user).exists():
                ctx['has_blog'] = True
                ctx['blog'] = Blog.objects.filter(owner=self.request.user)
        return ctx

class NewBlogPostView(CreateView):
    form_class = BlogPostForm
    template_name = 'blog_post.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(NewBlogPostView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        blog_post_obj = form.save(commit=False)
        blog_post_obj.blog = Blog.objects.get(owner=self.request.user)
        blog_post_obj.slug = slugify(blog_post_obj.title)
        blog_post_obj.is_published = True

        blog_post_obj.save()

        return HttpResponseRedirect(reverse('home'))

class UpdateBlogPostView(UpdateView):
    form_class = BlogPostForm
    template_name = 'blog_post.html'
    success_url = '/'
    model = BlogPost

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateBlogPostView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(UpdateBlogPostView, self).get_queryset()
        return queryset.filter(blog__owner=self.request.user)

class BlogPostDetailsView(DetailView):
    model = BlogPost
    template_name = 'blog_post_details.html'
