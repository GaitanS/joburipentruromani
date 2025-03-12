from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django_countries.fields import CountryField
from .models_subscription import SubscriptionPlan, CompanySubscription

class SubscriptionSelectForm(forms.Form):
    """Form for selecting a subscription plan"""
    plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        empty_label=None,
        widget=forms.RadioSelect,
        label=_('Select a Plan')
    )
    
    billing_cycle = forms.ChoiceField(
        choices=[
            ('monthly', _('Monthly Billing')),
            ('annual', _('Annual Billing (Save up to 20%)')),
        ],
        widget=forms.RadioSelect,
        label=_('Billing Cycle'),
        initial='monthly'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['plan'].queryset = self.fields['plan'].queryset.order_by('order')
        
        # Set labels with price information
        for radio in self.fields['plan'].widget.widgets:
            plan = radio.choice_value
            if plan and plan.isdigit():  # Make sure we have a valid plan ID
                plan_obj = SubscriptionPlan.objects.get(pk=int(plan))
                radio.choice_label = f"{plan_obj.name} - €{plan_obj.price_monthly}/mo"
        
class PaymentMethodForm(forms.Form):
    """Form for collecting payment method information"""
    # Cardholder details
    name = forms.CharField(
        label=_('Cardholder Name'),
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': _('As it appears on your card')})
    )
    
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'placeholder': _('For payment receipts')})
    )
    
    # Billing address
    address_line1 = forms.CharField(
        label=_('Address Line 1'),
        max_length=100,
    )
    
    address_line2 = forms.CharField(
        label=_('Address Line 2'),
        max_length=100,
        required=False,
    )
    
    city = forms.CharField(
        label=_('City'),
        max_length=100,
    )
    
    state = forms.CharField(
        label=_('State/Province'),
        max_length=100,
    )
    
    postal_code = forms.CharField(
        label=_('Postal Code'),
        max_length=20,
    )
    
    country = CountryField().formfield(
        label=_('Country'),
        initial='RO',
    )
    
    # Stripe elements token (populated by JS)
    stripe_payment_method_id = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('stripe_payment_method_id'):
            raise ValidationError(_('Payment method information is required.'))
        return cleaned_data

class SubscriptionUpgradeForm(forms.Form):
    """Form for upgrading/changing subscription"""
    new_plan = forms.ModelChoiceField(
        queryset=SubscriptionPlan.objects.filter(is_active=True),
        empty_label=None,
        widget=forms.RadioSelect,
        label=_('Select New Plan')
    )
    
    keep_billing_cycle = forms.BooleanField(
        initial=True,
        required=False,
        label=_('Keep current billing cycle'),
        help_text=_('If unchecked, you can select a new billing cycle below.')
    )
    
    billing_cycle = forms.ChoiceField(
        choices=[
            ('monthly', _('Monthly Billing')),
            ('annual', _('Annual Billing (Save up to 20%)')),
        ],
        widget=forms.RadioSelect,
        required=False,
        label=_('New Billing Cycle'),
        initial='monthly'
    )
    
    def __init__(self, *args, current_subscription=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_subscription = current_subscription
        
        # Set initial values based on current subscription
        if current_subscription:
            self.fields['billing_cycle'].initial = current_subscription.billing_cycle
            
            # Filter plans to show only upgrades or same tier for renewals
            if current_subscription.status in ['active', 'trialing']:
                current_plan = current_subscription.plan
                self.fields['new_plan'].queryset = SubscriptionPlan.objects.filter(
                    is_active=True
                ).exclude(tier='free').order_by('order')
                self.fields['new_plan'].initial = current_plan.id
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('keep_billing_cycle') and not cleaned_data.get('billing_cycle'):
            cleaned_data['billing_cycle'] = self.current_subscription.billing_cycle
        return cleaned_data
    
    def clean_new_plan(self):
        new_plan = self.cleaned_data.get('new_plan')
        if self.current_subscription and new_plan.id == self.current_subscription.plan.id:
            # No change in plan, this is a renewal
            pass
        return new_plan

class CancelSubscriptionForm(forms.Form):
    """Form for canceling a subscription"""
    confirm_cancellation = forms.BooleanField(
        label=_('I understand that canceling will end my subscription at the end of the current billing period'),
        required=True
    )
    
    reason = forms.ChoiceField(
        choices=[
            ('too_expensive', _('Too expensive')),
            ('missing_features', _('Missing features')),
            ('not_using', _('Not using enough')),
            ('found_alternative', _('Found a better alternative')),
            ('temporary', _('Temporary pause - will subscribe again')),
            ('other', _('Other reason')),
        ],
        label=_('Reason for cancellation'),
        required=True
    )
    
    feedback = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label=_('Additional feedback (optional)'),
        required=False
    )