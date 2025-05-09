from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, FormView
from django.db.models import Avg, Count
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from datetime import timedelta

from tour.models import Tour, Category as TourCategory, Destination
from blog.models import Post
from reviews.models import Review
from ..models import FAQ, ContactMessage, Newsletter, SiteSetting, Currency
from ..forms import ContactForm, NewsletterForm


class HomeView(TemplateView):
    """View for home page"""
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if Tour model has is_featured/is_popular fields, adjust if necessary
        context['featured_tours'] = Tour.objects.filter(is_active=True, is_featured=True)[:6]
        context['popular_tours'] = Tour.objects.filter(is_active=True).order_by('-view_count')[:6] # Assuming popularity based on views or rating
        context['tour_categories'] = TourCategory.objects.filter(is_active=True)[:6] # Use the imported Category (aliased or direct)
        context['latest_posts'] = Post.objects.filter(is_published=True).order_by('-published_at')[:3] # Use is_published and published_at
        context['featured_destinations'] = Destination.objects.filter(is_active=True, is_featured=True)[:6]

        # Get top reviews for testimonials section
        context['testimonials'] = Review.objects.filter(
            is_approved=True,
            rating__gte=4  # Only show reviews with 4 or 5 stars
        ).select_related('user', 'tour').order_by('-created_at')[:3]

        return context


class AboutView(TemplateView):
    """View for about us page"""
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['site_settings'] = SiteSetting.objects.first()
        except SiteSetting.DoesNotExist:
            context['site_settings'] = None
        return context


class FAQListView(ListView):
    """View for FAQ page"""
    model = FAQ
    template_name = 'core/faq.html'
    context_object_name = 'faqs'
    queryset = FAQ.objects.filter(is_active=True)


class ContactView(FormView):
    """View for contact page"""
    template_name = 'core/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        # Create the contact message
        contact_message = ContactMessage(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message']
        )
        contact_message.save()

        messages.success(self.request, _('Your message has been sent successfully. We will contact you soon!'))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['site_settings'] = SiteSetting.objects.first()
        except SiteSetting.DoesNotExist:
            context['site_settings'] = None
        return context


def subscribe_newsletter(request):
    """View to handle newsletter subscription"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Check if already subscribed
            if not Newsletter.objects.filter(email=email).exists():
                Newsletter.objects.create(email=email)
                messages.success(request, _('You have successfully subscribed to our newsletter!'))
            else:
                messages.info(request, _('You are already subscribed to our newsletter.'))

    # Redirect back to previous page
    return redirect(request.META.get('HTTP_REFERER', 'home'))


class TermsConditionsView(TemplateView):
    """View for terms and conditions page"""
    template_name = 'core/terms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['site_settings'] = SiteSetting.objects.first()
        except SiteSetting.DoesNotExist:
            context['site_settings'] = None
        return context


class PrivacyPolicyView(TemplateView):
    """View for privacy policy page"""
    template_name = 'core/privacy.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['site_settings'] = SiteSetting.objects.first()
        except SiteSetting.DoesNotExist:
            context['site_settings'] = None
        return context

@require_POST
def set_currency(request):
    """Sets the selected currency code in the session."""
    currency_code = request.POST.get('currency_code')
    next_url = request.POST.get('next', '/') # Default redirect to home

    # Validate if the currency code exists
    if currency_code and Currency.objects.filter(code=currency_code).exists():
        request.session['currency_code'] = currency_code
        messages.success(request, _(f"Currency set to {currency_code}."))
    else:
        messages.error(request, _("Invalid currency selected."))

    # Redirect back to the 'next' URL or the default
    return redirect(next_url)

def get_exchange_rates(request):
    """API endpoint to get current exchange rates for JavaScript"""
    try:
        # Get all active currencies
        currencies = Currency.objects.filter(is_active=True)

        # Check if rates need updating (older than 24 hours)
        oldest_update = currencies.order_by('last_updated').first()
        if oldest_update and (timezone.now() - oldest_update.last_updated) > timedelta(hours=24):
            # Rates are stale, but we'll still return them
            # The management command should be run separately
            pass

        # Format the response
        rates = {
            currency.code: {
                'code': currency.code,
                'name': currency.name,
                'symbol': currency.symbol,
                'rate': float(currency.exchange_rate)
            } for currency in currencies
        }

        return JsonResponse({
            'base_currency': 'USD',
            'rates': rates,
            'last_updated': oldest_update.last_updated.isoformat() if oldest_update else None
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
