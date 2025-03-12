from django.urls import path
from . import views
from . import views_subscription
from . import views_blog

app_name = 'jobs'

urlpatterns = [
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<slug:slug>/', views.job_detail, name='job_detail'),
    path('jobs/<slug:slug>/apply/', views.apply_job, name='apply_job'),
    path('application/<int:application_id>/confirmation/', views.application_confirmation, name='application_confirmation'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('companies/<slug:slug>/', views.company_detail, name='company_detail'),
    path('search/', views.search_results, name='search_results'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('company/dashboard/', views.company_dashboard, name='company_dashboard'),
    path('about/', views.about, name='about'),
    path('for-companies/', views.for_companies, name='for_companies'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    
    # Subscription urls
    path('subscription/plans/', views_subscription.subscription_plans, name='subscription_plans'),
    path('subscription/payment/', views_subscription.subscription_payment, name='subscription_payment'),
    path('subscription/success/', views_subscription.subscription_success, name='subscription_success'),
    path('subscription/dashboard/', views_subscription.subscription_dashboard, name='subscription_dashboard'),
    path('subscription/billing/', views_subscription.subscription_billing, name='subscription_billing'),
    path('subscription/upgrade/', views_subscription.subscription_upgrade, name='subscription_upgrade'),
    path('subscription/cancel/', views_subscription.subscription_cancel, name='subscription_cancel'),
    
    # Payment methods
    path('subscription/payment-method/add/', views_subscription.add_payment_method, name='add_payment_method'),
    path('subscription/payment-method/remove/<str:payment_method_id>/', views_subscription.remove_payment_method, name='remove_payment_method'),
    
    # Stripe webhook
    path('subscription/stripe-webhook/', views_subscription.stripe_webhook, name='stripe_webhook'),
    
    # Blog URLs
    path('blog/', views_blog.BlogHomeView.as_view(), name='blog_home'),
    path('blog/category/<slug:slug>/', views_blog.BlogCategoryView.as_view(), name='blog_category'),
    path('blog/tag/<slug:slug>/', views_blog.BlogTagView.as_view(), name='blog_tag'),
    path('blog/search/', views_blog.BlogSearchView.as_view(), name='blog_search'),
    path('blog/<slug:slug>/', views_blog.BlogDetailView.as_view(), name='blog_detail'),
    
    # Blog admin (staff only)
    path('admin/blog/', views_blog.BlogAdminListView.as_view(), name='blog_admin'),
    path('admin/blog/new/', views_blog.BlogAdminCreateView.as_view(), name='blog_create'),
    path('admin/blog/<int:pk>/edit/', views_blog.BlogAdminUpdateView.as_view(), name='blog_edit'),
    path('admin/blog/<int:pk>/delete/', views_blog.BlogAdminDeleteView.as_view(), name='blog_delete'),
    path('admin/blog/comments/', views_blog.BlogCommentAdminView.as_view(), name='blog_comments_admin'),
]