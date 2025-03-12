import stripe
import json
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from datetime import timedelta
from .models import Company
from .models_subscription import (
    SubscriptionPlan, 
    CompanySubscription, 
    SubscriptionPayment,
    StripeWebhookEvent
)
from .forms_subscription import (
    SubscriptionSelectForm,
    PaymentMethodForm,
    SubscriptionUpgradeForm,
    CancelSubscriptionForm
)

# Initialize Stripe with API key
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def subscription_plans(request):
    """Display available subscription plans to the user"""
    try:
        company = request.user.company
    except:
        messages.error(request, _('You need a company profile to subscribe to a plan.'))
        return redirect('jobs:home')
    
    # Check if company already has an active subscription
    try:
        active_subscription = company.subscription
        if active_subscription.is_active():
            messages.info(request, _('You already have an active subscription. You can manage it from your dashboard.'))
            return redirect('jobs:subscription_dashboard')
    except CompanySubscription.DoesNotExist:
        pass
    
    # Get all active plans
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('order')
    
    # Initialize form
    form = SubscriptionSelectForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        selected_plan = form.cleaned_data['plan']
        billing_cycle = form.cleaned_data['billing_cycle']
        
        # Store in session for payment step
        request.session['selected_plan_id'] = selected_plan.id
        request.session['selected_billing_cycle'] = billing_cycle
        
        return redirect('jobs:subscription_payment')
    
    context = {
        'plans': plans,
        'form': form,
    }
    return render(request, 'jobs/subscription/plans.html', context)

@login_required
def subscription_payment(request):
    """Handle payment information collection for subscription"""
    try:
        company = request.user.company
    except:
        messages.error(request, _('You need a company profile to subscribe to a plan.'))
        return redirect('jobs:home')
    
    # Get selected plan from session
    plan_id = request.session.get('selected_plan_id')
    billing_cycle = request.session.get('selected_billing_cycle', 'monthly')
    
    if not plan_id:
        messages.error(request, _('Please select a plan first.'))
        return redirect('jobs:subscription_plans')
    
    # Get plan details
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    # Determine price based on billing cycle
    if billing_cycle == 'annual':
        price = plan.price_annually
        stripe_price_id = plan.stripe_annual_price_id
    else:
        price = plan.price_monthly
        stripe_price_id = plan.stripe_monthly_price_id
    
    # Handle free plan
    if plan.is_free:
        return redirect('jobs:subscription_success')
    
    # Initialize form
    form = PaymentMethodForm(request.POST or None, initial={
        'name': request.user.get_full_name(),
        'email': request.user.email,
    })
    
    if request.method == 'POST' and form.is_valid():
        try:
            # Get Stripe token from form
            payment_method_id = form.cleaned_data['stripe_payment_method_id']
            
            # Create or get Stripe customer
            if company.subscription and company.subscription.stripe_customer_id:
                customer = stripe.Customer.retrieve(company.subscription.stripe_customer_id)
            else:
                # Create new customer
                customer = stripe.Customer.create(
                    email=request.user.email,
                    name=form.cleaned_data['name'],
                    payment_method=payment_method_id,
                    invoice_settings={'default_payment_method': payment_method_id},
                    address={
                        'line1': form.cleaned_data['address_line1'],
                        'line2': form.cleaned_data['address_line2'],
                        'city': form.cleaned_data['city'],
                        'state': form.cleaned_data['state'],
                        'postal_code': form.cleaned_data['postal_code'],
                        'country': form.cleaned_data['country'],
                    },
                )
            
            # Create subscription in Stripe
            stripe_subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[
                    {"price": stripe_price_id},
                ],
                payment_behavior='default_incomplete',
                payment_settings={'save_default_payment_method': 'on_subscription'},
                expand=['latest_invoice.payment_intent'],
            )
            
            # Save subscription details in session for success page
            request.session['stripe_subscription_id'] = stripe_subscription.id
            request.session['subscription_plan_id'] = plan.id
            request.session['subscription_billing_cycle'] = billing_cycle
            request.session['stripe_customer_id'] = customer.id
            
            # Return client secret for payment confirmation
            return JsonResponse({
                'client_secret': stripe_subscription.latest_invoice.payment_intent.client_secret,
                'subscription_id': stripe_subscription.id,
            })
            
        except stripe.error.StripeError as e:
            # Handle Stripe errors
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            # Handle other errors
            return JsonResponse({'error': _('An unexpected error occurred. Please try again.')}, status=500)
    
    context = {
        'form': form,
        'plan': plan,
        'billing_cycle': billing_cycle,
        'price': price,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'jobs/subscription/payment.html', context)

@login_required
def subscription_success(request):
    """Handle successful subscription creation/payment"""
    try:
        company = request.user.company
    except:
        messages.error(request, _('You need a company profile to subscribe to a plan.'))
        return redirect('jobs:home')
    
    # Get subscription data from session
    stripe_subscription_id = request.session.get('stripe_subscription_id')
    plan_id = request.session.get('subscription_plan_id')
    billing_cycle = request.session.get('subscription_billing_cycle', 'monthly')
    stripe_customer_id = request.session.get('stripe_customer_id')
    
    if not plan_id:
        messages.error(request, _('No subscription information found.'))
        return redirect('jobs:subscription_plans')
    
    # Get plan details
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    # Handle free plan
    if plan.is_free:
        try:
            # Create or update subscription
            with transaction.atomic():
                # Check if subscription already exists
                try:
                    subscription = company.subscription
                    subscription.plan = plan
                    subscription.status = 'active'
                    subscription.billing_cycle = billing_cycle
                    subscription.start_date = timezone.now()
                    subscription.end_date = timezone.now() + timedelta(days=365 if billing_cycle == 'annual' else 30)
                    subscription.save()
                except CompanySubscription.DoesNotExist:
                    # Create new subscription
                    subscription = CompanySubscription.objects.create(
                        company=company,
                        plan=plan,
                        status='active',
                        billing_cycle=billing_cycle,
                        start_date=timezone.now(),
                        end_date=timezone.now() + timedelta(days=365 if billing_cycle == 'annual' else 30)
                    )
                
                messages.success(request, _('Your free plan has been activated.'))
                return redirect('jobs:subscription_dashboard')
        except Exception as e:
            messages.error(request, f'Error activating free plan: {str(e)}')
            return redirect('jobs:subscription_plans')
    
    # For paid plans, verify the subscription with Stripe
    if stripe_subscription_id:
        try:
            # Get subscription details from Stripe
            stripe_subscription = stripe.Subscription.retrieve(stripe_subscription_id)
            
            # Ensure the subscription is active
            if stripe_subscription.status not in ['active', 'trialing']:
                messages.warning(request, _('Your subscription is not yet active. Please check your payment details.'))
                return redirect('jobs:subscription_payment')
            
            # Calculate end date based on billing cycle
            if billing_cycle == 'annual':
                end_date = timezone.now() + timedelta(days=365)
            else:
                end_date = timezone.now() + timedelta(days=30)
            
            # Create or update subscription in our database
            with transaction.atomic():
                # Check if subscription already exists
                try:
                    subscription = company.subscription
                    subscription.plan = plan
                    subscription.stripe_customer_id = stripe_customer_id
                    subscription.stripe_subscription_id = stripe_subscription_id
                    subscription.status = 'active'
                    subscription.billing_cycle = billing_cycle
                    subscription.start_date = timezone.now()
                    subscription.end_date = end_date
                    subscription.auto_renew = True
                    subscription.save()
                except CompanySubscription.DoesNotExist:
                    # Create new subscription
                    subscription = CompanySubscription.objects.create(
                        company=company,
                        plan=plan,
                        stripe_customer_id=stripe_customer_id,
                        stripe_subscription_id=stripe_subscription_id,
                        status='active',
                        billing_cycle=billing_cycle,
                        start_date=timezone.now(),
                        end_date=end_date,
                        auto_renew=True
                    )
                
                # Create payment record
                SubscriptionPayment.objects.create(
                    subscription=subscription,
                    payment_id=stripe_subscription.latest_invoice,
                    amount=plan.price_annually if billing_cycle == 'annual' else plan.price_monthly,
                    currency='EUR',
                    status='succeeded',
                    payment_method='card',
                    is_successful=True,
                    transaction_data={'subscription_id': stripe_subscription_id}
                )
            
            # Clear session data
            for key in ['stripe_subscription_id', 'subscription_plan_id', 'subscription_billing_cycle', 'stripe_customer_id']:
                if key in request.session:
                    del request.session[key]
            
            messages.success(request, _('Your subscription has been successfully activated!'))
            return redirect('jobs:subscription_dashboard')
            
        except stripe.error.StripeError as e:
            messages.error(request, f'Stripe error: {str(e)}')
            return redirect('jobs:subscription_payment')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('jobs:subscription_payment')
    
    # Fallback - show general success page with link to dashboard
    return render(request, 'jobs/subscription/success.html', {'plan': plan})

@login_required
def subscription_dashboard(request):
    """Display subscription dashboard for company"""
    try:
        company = request.user.company
    except:
        messages.error(request, _('You need a company profile to access the subscription dashboard.'))
        return redirect('jobs:home')
    
    # Get active subscription
    try:
        subscription = company.subscription
    except CompanySubscription.DoesNotExist:
        # No subscription, redirect to plans
        messages.info(request, _('You don\'t have an active subscription. Please select a plan.'))
        return redirect('jobs:subscription_plans')
    
    # Get usage data
    active_jobs_count = subscription.active_jobs_count()
    jobs_remaining = subscription.plan.max_active_jobs - active_jobs_count if subscription.plan.max_active_jobs > 0 else 'Unlimited'
    remaining_promoted = subscription.remaining_promoted_listings()
    days_remaining = subscription.days_remaining()
    
    # Get recent payments
    recent_payments = SubscriptionPayment.objects.filter(
        subscription=subscription,
        is_successful=True
    ).order_by('-payment_date')[:5]
    
    context = {
        'subscription': subscription,
        'active_jobs_count': active_jobs_count,
        'jobs_remaining': jobs_remaining,
        'remaining_promoted': remaining_promoted,
        'days_remaining': days_remaining,
        'recent_payments': recent_payments,
    }
    return render(request, 'jobs/subscription/dashboard.html', context)

@login_required
def subscription_billing(request):
    """Display billing history and payment methods"""
    try:
        company = request.user.company
        subscription = company.subscription
    except:
        messages.error(request, _('You need an active subscription to access billing information.'))
        return redirect('jobs:subscription_plans')
    
    # Get payment history
    payments = SubscriptionPayment.objects.filter(subscription=subscription).order_by('-payment_date')
    
    # Get payment methods from Stripe
    payment_methods = []
    if subscription.stripe_customer_id:
        try:
            methods = stripe.PaymentMethod.list(
                customer=subscription.stripe_customer_id,
                type='card'
            )
            payment_methods = methods.data
        except stripe.error.StripeError:
            messages.warning(request, _('Could not retrieve payment methods.'))
    
    context = {
        'subscription': subscription,
        'payments': payments,
        'payment_methods': payment_methods,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'jobs/subscription/billing.html', context)

@login_required
def subscription_upgrade(request):
    """Handle subscription plan changes (upgrades/downgrades)"""
    try:
        company = request.user.company
        subscription = company.subscription
    except:
        messages.error(request, _('You need an active subscription to upgrade.'))
        return redirect('jobs:subscription_plans')
    
    # Initialize form
    form = SubscriptionUpgradeForm(
        request.POST or None,
        current_subscription=subscription
    )
    
    if request.method == 'POST' and form.is_valid():
        new_plan = form.cleaned_data['new_plan']
        keep_billing_cycle = form.cleaned_data['keep_billing_cycle']
        billing_cycle = subscription.billing_cycle if keep_billing_cycle else form.cleaned_data['billing_cycle']
        
        # Store in session for next step
        request.session['upgrade_plan_id'] = new_plan.id
        request.session['upgrade_billing_cycle'] = billing_cycle
        
        # Check if this is a significant change requiring payment
        if new_plan.tier == 'free':
            # Downgrading to free - no payment needed
            with transaction.atomic():
                # Cancel existing Stripe subscription if it exists
                if subscription.stripe_subscription_id:
                    try:
                        stripe.Subscription.delete(subscription.stripe_subscription_id)
                    except stripe.error.StripeError:
                        pass
                
                # Update subscription
                subscription.plan = new_plan
                subscription.status = 'active'
                subscription.billing_cycle = billing_cycle
                subscription.stripe_subscription_id = None
                subscription.auto_renew = False
                subscription.save()
            
            messages.success(request, _('Your subscription has been downgraded to the free plan.'))
            return redirect('jobs:subscription_dashboard')
        
        # For paid plans
        try:
            # If plan is changing
            if new_plan.id != subscription.plan.id:
                # Has Stripe subscription to update
                if subscription.stripe_subscription_id:
                    # Get appropriate price ID
                    price_id = new_plan.stripe_annual_price_id if billing_cycle == 'annual' else new_plan.stripe_monthly_price_id
                    
                    # Update Stripe subscription
                    stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                    items = [{
                        'id': stripe_subscription['items']['data'][0].id,
                        'price': price_id,
                    }]
                    
                    # Update subscription with proration
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        items=items,
                        proration_behavior='always_invoice',
                    )
                    
                    # Update our subscription record
                    subscription.plan = new_plan
                    subscription.billing_cycle = billing_cycle
                    subscription.save()
                    
                    messages.success(request, _('Your subscription has been updated successfully.'))
                    return redirect('jobs:subscription_dashboard')
                else:
                    # No Stripe subscription, needs to create new one
                    return redirect('jobs:subscription_payment')
            else:
                # Plan not changing, just billing cycle
                if subscription.billing_cycle != billing_cycle and subscription.stripe_subscription_id:
                    # Update billing cycle in Stripe
                    price_id = new_plan.stripe_annual_price_id if billing_cycle == 'annual' else new_plan.stripe_monthly_price_id
                    
                    stripe_subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                    items = [{
                        'id': stripe_subscription['items']['data'][0].id,
                        'price': price_id,
                    }]
                    
                    # Update subscription with proration
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        items=items,
                        proration_behavior='always_invoice',
                    )
                    
                    # Update our subscription record
                    subscription.billing_cycle = billing_cycle
                    subscription.save()
                    
                    messages.success(request, _('Your billing cycle has been updated successfully.'))
                    return redirect('jobs:subscription_dashboard')
                else:
                    # No changes
                    messages.info(request, _('No changes were made to your subscription.'))
                    return redirect('jobs:subscription_dashboard')
        except stripe.error.StripeError as e:
            messages.error(request, f'Stripe error: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    context = {
        'form': form,
        'subscription': subscription,
        'available_plans': SubscriptionPlan.objects.filter(is_active=True).exclude(tier='free'),
    }
    return render(request, 'jobs/subscription/upgrade.html', context)

@login_required
def subscription_cancel(request):
    """Handle subscription cancellation"""
    try:
        company = request.user.company
        subscription = company.subscription
    except:
        messages.error(request, _('You need an active subscription to cancel.'))
        return redirect('jobs:home')
    
    if subscription.status not in ['active', 'trialing']:
        messages.info(request, _('Your subscription is not active.'))
        return redirect('jobs:subscription_dashboard')
    
    form = CancelSubscriptionForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        reason = form.cleaned_data['reason']
        feedback = form.cleaned_data['feedback']
        
        # Store cancellation reason
        # You might want to create a model to store this feedback
        
        # Cancel in Stripe
        if subscription.stripe_subscription_id:
            try:
                # Cancel at period end - this keeps the subscription active until the end of the period
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                
                # Update our record
                subscription.auto_renew = False
                subscription.save()
                
                messages.success(request, _('Your subscription has been cancelled and will end at the end of your current billing period.'))
                return redirect('jobs:subscription_dashboard')
            except stripe.error.StripeError as e:
                messages.error(request, f'Error with Stripe: {str(e)}')
        else:
            # No Stripe subscription, just update our record
            subscription.status = 'canceled'
            subscription.auto_renew = False
            subscription.save()
            
            messages.success(request, _('Your subscription has been cancelled.'))
            return redirect('jobs:subscription_dashboard')
    
    context = {
        'form': form,
        'subscription': subscription,
    }
    return render(request, 'jobs/subscription/cancel.html', context)

@login_required
def add_payment_method(request):
    """Add new payment method to customer account"""
    try:
        company = request.user.company
        subscription = company.subscription
    except:
        return JsonResponse({'error': _('You need an active subscription to add a payment method.')}, status=400)
    
    if not subscription.stripe_customer_id:
        return JsonResponse({'error': _('No Stripe customer record found.')}, status=400)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            payment_method_id = data.get('payment_method_id')
            
            if not payment_method_id:
                return JsonResponse({'error': _('No payment method provided.')}, status=400)
            
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=subscription.stripe_customer_id,
            )
            
            # Update customer's default payment method
            stripe.Customer.modify(
                subscription.stripe_customer_id,
                invoice_settings={
                    'default_payment_method': payment_method_id,
                },
            )
            
            return JsonResponse({'success': True})
        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': _('Invalid request method.')}, status=405)

@login_required
def remove_payment_method(request, payment_method_id):
    """Remove payment method from customer account"""
    try:
        company = request.user.company
        subscription = company.subscription
    except:
        messages.error(request, _('You need an active subscription to manage payment methods.'))
        return redirect('jobs:subscription_dashboard')
    
    if not subscription.stripe_customer_id:
        messages.error(request, _('No Stripe customer record found.'))
        return redirect('jobs:subscription_billing')
    
    try:
        # Detach payment method
        stripe.PaymentMethod.detach(payment_method_id)
        messages.success(request, _('Payment method has been removed.'))
    except stripe.error.StripeError as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('jobs:subscription_billing')

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    if not sig_header:
        return HttpResponse(status=400)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)
    
    # Store event for logging/debugging
    StripeWebhookEvent.objects.create(
        webhook_id=event['id'],
        event_type=event['type'],
        event_data=event
    )
    
    # Handle specific event types
    if event['type'] == 'invoice.payment_succeeded':
        handle_payment_succeeded(event)
    elif event['type'] == 'invoice.payment_failed':
        handle_payment_failed(event)
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event)
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event)
    
    return HttpResponse(status=200)

def handle_payment_succeeded(event):
    """Handle successful payment webhook"""
    invoice = event['data']['object']
    subscription_id = invoice.get('subscription')
    
    if not subscription_id:
        return
    
    try:
        subscription = CompanySubscription.objects.get(stripe_subscription_id=subscription_id)
        
        # Create payment record
        SubscriptionPayment.objects.create(
            subscription=subscription,
            payment_id=invoice['id'],
            amount=invoice['amount_paid'] / 100,  # Convert from cents
            currency=invoice['currency'].upper(),
            status='succeeded',
            payment_method=invoice.get('payment_method_types', ['unknown'])[0],
            is_successful=True,
            transaction_data={'invoice_id': invoice['id']}
        )
        
        # Update subscription status
        subscription.status = 'active'
        
        # Update end date based on billing cycle
        if subscription.billing_cycle == 'annual':
            subscription.end_date = timezone.now() + timedelta(days=365)
        else:
            subscription.end_date = timezone.now() + timedelta(days=30)
        
        subscription.save()
    except CompanySubscription.DoesNotExist:
        # Subscription not found in our database
        pass

def handle_payment_failed(event):
    """Handle failed payment webhook"""
    invoice = event['data']['object']
    subscription_id = invoice.get('subscription')
    
    if not subscription_id:
        return
    
    try:
        subscription = CompanySubscription.objects.get(stripe_subscription_id=subscription_id)
        
        # Create payment record
        SubscriptionPayment.objects.create(
            subscription=subscription,
            payment_id=invoice['id'],
            amount=invoice['amount_due'] / 100,  # Convert from cents
            currency=invoice['currency'].upper(),
            status='failed',
            payment_method=invoice.get('payment_method_types', ['unknown'])[0],
            is_successful=False,
            transaction_data={'invoice_id': invoice['id']}
        )
        
        # Update subscription status
        subscription.status = 'past_due'
        subscription.save()
        
        # TODO: Send email notification about failed payment
    except CompanySubscription.DoesNotExist:
        # Subscription not found in our database
        pass

def handle_subscription_deleted(event):
    """Handle subscription deletion webhook"""
    subscription_data = event['data']['object']
    subscription_id = subscription_data['id']
    
    try:
        subscription = CompanySubscription.objects.get(stripe_subscription_id=subscription_id)
        subscription.status = 'canceled'
        subscription.auto_renew = False
        subscription.save()
        
        # TODO: Send email notification about subscription cancellation
    except CompanySubscription.DoesNotExist:
        # Subscription not found in our database
        pass

def handle_subscription_updated(event):
    """Handle subscription update webhook"""
    subscription_data = event['data']['object']
    subscription_id = subscription_data['id']
    
    try:
        subscription = CompanySubscription.objects.get(stripe_subscription_id=subscription_id)
        
        # Update status
        stripe_status = subscription_data['status']
        if stripe_status == 'active':
            subscription.status = 'active'
        elif stripe_status == 'past_due':
            subscription.status = 'past_due'
        elif stripe_status == 'canceled':
            subscription.status = 'canceled'
        elif stripe_status == 'trialing':
            subscription.status = 'trialing'
        elif stripe_status == 'unpaid':
            subscription.status = 'past_due'
        
        subscription.save()
    except CompanySubscription.DoesNotExist:
        # Subscription not found in our database
        pass