from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .models import Job, Category, Company, Location, Application, UserProfile, SubscriptionPlan
from .forms import UserRegistrationForm, CompanyRegistrationForm, JobSeekerProfileForm


def home(request):
    """Homepage with search, categories, and featured jobs"""
    categories = Category.objects.all()[:6]  # Limiting to 6 categories for the homepage
    featured_jobs = Job.objects.filter(status='active', is_featured=True)[:3]
    recent_jobs = Job.objects.filter(status='active').order_by('-created_at')[:6]
    
    context = {
        'categories': categories,
        'featured_jobs': featured_jobs,
        'recent_jobs': recent_jobs,
    }
    return render(request, 'jobs/home.html', context)


def job_list(request):
    """Job listing page with search and filtering"""
    jobs_list = Job.objects.filter(status='active')
    categories = Category.objects.all()
    locations = Location.objects.all()
    
    # Search functionality
    query = request.GET.get('q')
    location = request.GET.get('location')
    category = request.GET.get('category')
    job_type = request.GET.get('job_type')
    
    if query:
        jobs_list = jobs_list.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(requirements__icontains=query) |
            Q(company__name__icontains=query)
        )
    
    if location:
        jobs_list = jobs_list.filter(location__city__icontains=location)
    
    if category:
        jobs_list = jobs_list.filter(category__slug=category)
    
    if job_type:
        jobs_list = jobs_list.filter(job_type=job_type)
    
    # Pagination
    paginator = Paginator(jobs_list, 10)  # Show 10 jobs per page
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    context = {
        'jobs': jobs,
        'categories': categories,
        'locations': locations,
        'query': query,
        'selected_location': location,
        'selected_category': category,
        'selected_job_type': job_type,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, slug):
    """Job detail page"""
    job = get_object_or_404(Job, slug=slug, status='active')
    related_jobs = Job.objects.filter(
        category=job.category, 
        status='active'
    ).exclude(id=job.id)[:3]
    
    # Check if user has already applied
    has_applied = False
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, user=request.user).exists()
    
    context = {
        'job': job,
        'related_jobs': related_jobs,
        'has_applied': has_applied,
    }
    return render(request, 'jobs/job_detail.html', context)


def category_detail(request, slug):
    """Category detail page with jobs in that category"""
    category = get_object_or_404(Category, slug=slug)
    jobs_list = Job.objects.filter(category=category, status='active')
    
    # Pagination
    paginator = Paginator(jobs_list, 10)  # Show 10 jobs per page
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    context = {
        'category': category,
        'jobs': jobs,
    }
    return render(request, 'jobs/category_detail.html', context)


def company_detail(request, slug):
    """Company detail page with jobs from that company"""
    company = get_object_or_404(Company, slug=slug)
    jobs = Job.objects.filter(company=company, status='active')
    
    context = {
        'company': company,
        'jobs': jobs,
    }
    return render(request, 'jobs/company_detail.html', context)


@login_required
def apply_job(request, slug):
    """Job application form handling"""
    job = get_object_or_404(Job, slug=slug, status='active')
    
    # Check if user has already applied
    if Application.objects.filter(job=job, user=request.user).exists():
        messages.info(request, _('Ai aplicat deja pentru acest job.'))
        return redirect('jobs:job_detail', slug=job.slug)
    
    if request.method == 'POST':
        resume = request.FILES.get('resume')
        cover_letter = request.POST.get('cover_letter', '')
        
        if not resume:
            messages.error(request, _('CV-ul este obligatoriu.'))
            return redirect('jobs:job_detail', slug=job.slug)
        
        # Create application
        application = Application.objects.create(
            job=job,
            user=request.user,
            resume=resume,
            cover_letter=cover_letter
        )
        
        messages.success(request, _('Aplicarea ta a fost trimisă cu succes!'))
        return redirect('jobs:application_confirmation', application_id=application.id)
    
    return redirect('jobs:job_detail', slug=job.slug)


@login_required
def application_confirmation(request, application_id):
    """Confirmation page after successful application"""
    application = get_object_or_404(Application, id=application_id, user=request.user)
    
    context = {
        'application': application,
    }
    return render(request, 'jobs/application_confirmation.html', context)


@login_required
def user_dashboard(request):
    """User dashboard showing applied jobs"""
    applications = Application.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'applications': applications,
    }
    return render(request, 'jobs/user_dashboard.html', context)


@login_required
def company_dashboard(request):
    """Company dashboard showing posted jobs and applications"""
    try:
        company = request.user.company
        jobs = Job.objects.filter(company=company)
        applications = Application.objects.filter(job__company=company).order_by('-created_at')
        
        context = {
            'company': company,
            'jobs': jobs,
            'applications': applications,
        }
        return render(request, 'jobs/company_dashboard.html', context)
    except:
        messages.error(request, _('Nu ai un profil de companie. Contactează administratorul.'))
        return redirect('jobs:home')


def search_results(request):
    """Advanced search results page"""
    return job_list(request)  # Reuse job_list view with different template


def about(request):
    """About us page"""
    context = {
        'title': 'Despre noi',
    }
    return render(request, 'pages/about.html', context)


def for_companies(request):
    """Page for companies/employers"""
    context = {
        'title': 'Pentru companii',
    }
    return render(request, 'pages/for_companies.html', context)


def subscription_plans(request):
    """Page displaying subscription plans and pricing for companies"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order')
    
    context = {
        'title': 'Planuri de Abonament',
        'plans': plans,
    }
    return render(request, 'subscriptions/plans.html', context)


def terms(request):
    """Terms and Conditions page"""
    context = {
        'title': 'Termeni și Condiții',
        'current_date': datetime.now().strftime('%d/%m/%Y')
    }
    return render(request, 'pages/terms.html', context)


def privacy(request):
    """Privacy Policy page"""
    context = {
        'title': 'Politica de Confidențialitate',
        'current_date': datetime.now().strftime('%d/%m/%Y')
    }
    return render(request, 'pages/privacy.html', context)


def register(request):
    """User registration page"""
    if request.user.is_authenticated:
        return redirect('jobs:home')
    
    error_message = None
    
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'job_seeker':
            form = UserRegistrationForm(request.POST)
            
            # Validate terms agreement
            terms_agreement = request.POST.get('terms')
            if not terms_agreement:
                form.add_error('terms', _('Trebuie să fiți de acord cu Termenii și Condițiile pentru a continua.'))
            
            if form.is_valid():
                try:
                    user = form.save()
                    
                    # Create user profile
                    profile = UserProfile(
                        user=user,
                        phone=form.cleaned_data.get('phone', '')
                    )
                    profile.save()
                    
                    # Log in the user
                    username = form.cleaned_data.get('username')
                    password = form.cleaned_data.get('password1')
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    
                    messages.success(request, _('Contul tău a fost creat cu succes!'))
                    return redirect('jobs:user_dashboard')
                except Exception as e:
                    error_message = str(e)
        
        elif user_type == 'employer':
            form = CompanyRegistrationForm(request.POST)
            
            # Validate terms agreement
            terms_agreement = request.POST.get('terms')
            if not terms_agreement:
                form.add_error('terms', _('Trebuie să fiți de acord cu Termenii și Condițiile pentru a continua.'))
            
            if form.is_valid():
                try:
                    user = form.save()
                    
                    # Create company
                    company = Company(
                        user=user,
                        name=form.cleaned_data.get('company_name'),
                        website=form.cleaned_data.get('website', ''),
                        slug=form.cleaned_data.get('company_name').lower().replace(' ', '-')
                    )
                    company.save()
                    
                    # Log in the user
                    username = form.cleaned_data.get('username')
                    password = form.cleaned_data.get('password1')
                    user = authenticate(username=username, password=password)
                    login(request, user)
                    
                    messages.success(request, _('Contul companiei a fost creat cu succes!'))
                    return redirect('jobs:company_dashboard')
                except Exception as e:
                    error_message = str(e)
        
        # If form is invalid, it will be handled in template
        if error_message:
            messages.error(request, _(f'Eroare la înregistrare: {error_message}'))
    
    context = {
        'title': 'Înregistrare',
    }
    return render(request, 'auth/register.html', context)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'auth/password_reset_form.html'
    email_template_name = 'auth/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'
