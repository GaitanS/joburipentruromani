# Generated by Django 5.1.6 on 2025-03-12 13:06

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_location_country'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeWebhookEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('webhook_id', models.CharField(max_length=100, unique=True)),
                ('event_type', models.CharField(max_length=100)),
                ('event_data', models.JSONField()),
                ('processed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Stripe Webhook Event',
                'verbose_name_plural': 'Stripe Webhook Events',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tier', models.CharField(choices=[('free', 'Free'), ('standard', 'Standard'), ('business', 'Business'), ('enterprise', 'Enterprise'), ('promoted_only', 'Promoted Only')], max_length=20, verbose_name='Tier')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('description', models.TextField(verbose_name='Description')),
                ('price_monthly', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Monthly Price (EUR)')),
                ('price_annually', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Annual Price (EUR)')),
                ('max_active_jobs', models.IntegerField(default=1, verbose_name='Maximum Active Job Listings')),
                ('job_visibility_days', models.IntegerField(default=30, verbose_name='Job Visibility Days')),
                ('has_candidate_cv_access', models.BooleanField(default=True, verbose_name='Candidate CV Access')),
                ('promoted_listings_count', models.IntegerField(default=0, verbose_name='Included Promoted Listings')),
                ('has_priority_support', models.BooleanField(default=False, verbose_name='Priority Support')),
                ('stripe_monthly_price_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='Stripe Monthly Price ID')),
                ('stripe_annual_price_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='Stripe Annual Price ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('order', models.IntegerField(default=0, verbose_name='Display Order')),
            ],
            options={
                'verbose_name': 'Subscription Plan',
                'verbose_name_plural': 'Subscription Plans',
                'ordering': ['order'],
            },
        ),
        migrations.AlterField(
            model_name='adplacement',
            name='position',
            field=models.CharField(choices=[('header', 'Sub Header'), ('between_categories', 'Între Categorii și Joburi'), ('sidebar', 'Sidebar'), ('job_listing', 'Între Listări de Joburi'), ('job_detail', 'Sub Detalii Job'), ('footer', 'Footer'), ('user_dashboard', 'Dashboard Utilizator'), ('company_dashboard', 'Dashboard Companie'), ('after_apply', 'După Aplicare'), ('subscription_top', 'Pagini Abonament - Sus'), ('subscription_bottom', 'Pagini Abonament - Jos'), ('subscription_sidebar', 'Pagini Abonament - Sidebar'), ('subscription_success', 'Pagină Succes Abonament')], max_length=50, verbose_name='Poziție'),
        ),
        migrations.CreateModel(
            name='CompanySubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_customer_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='Stripe Customer ID')),
                ('stripe_subscription_id', models.CharField(blank=True, max_length=100, null=True, verbose_name='Stripe Subscription ID')),
                ('status', models.CharField(choices=[('active', 'Active'), ('past_due', 'Past Due'), ('canceled', 'Canceled'), ('trialing', 'Trialing'), ('expired', 'Expired')], default='active', max_length=20, verbose_name='Status')),
                ('billing_cycle', models.CharField(choices=[('monthly', 'Monthly'), ('annual', 'Annual')], default='monthly', max_length=20, verbose_name='Billing Cycle')),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Start Date')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='End Date')),
                ('is_trial', models.BooleanField(default=False, verbose_name='Is Trial')),
                ('trial_end_date', models.DateTimeField(blank=True, null=True, verbose_name='Trial End Date')),
                ('auto_renew', models.BooleanField(default=False, verbose_name='Auto Renew')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='jobs.company')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='subscriptions', to='jobs.subscriptionplan')),
            ],
            options={
                'verbose_name': 'Company Subscription',
                'verbose_name_plural': 'Company Subscriptions',
            },
        ),
        migrations.CreateModel(
            name='SubscriptionPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_id', models.CharField(max_length=100, unique=True, verbose_name='Payment ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Amount')),
                ('currency', models.CharField(default='EUR', max_length=3, verbose_name='Currency')),
                ('status', models.CharField(max_length=20, verbose_name='Status')),
                ('payment_method', models.CharField(max_length=50, verbose_name='Payment Method')),
                ('payment_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Payment Date')),
                ('is_successful', models.BooleanField(default=False, verbose_name='Is Successful')),
                ('transaction_data', models.JSONField(blank=True, null=True, verbose_name='Transaction Data')),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='jobs.companysubscription')),
            ],
            options={
                'verbose_name': 'Subscription Payment',
                'verbose_name_plural': 'Subscription Payments',
            },
        ),
    ]
