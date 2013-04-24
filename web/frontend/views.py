import uuid

from django import forms
from django.http import (HttpResponseRedirect, HttpResponse,
                         HttpResponseBadRequest, Http404,
                         HttpResponseForbidden)
from django.shortcuts import render_to_response, redirect
from django.contrib import auth
from django.shortcuts import get_object_or_404
from django.conf import settings
from frontend.forms import SigninForm, UserProfileForm, SearchForm, ResendActivationEmailForm, DataEnquiryForm
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
# https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from tagging.models import Tag, TaggedItem
from tagging.utils import get_tag, calculate_cloud, get_tag_list, LOGARITHMIC, get_queryset_and_model

from codewiki.models import (Code, UserCodeRole, Scraper, View, scraper_search_query, user_search_query, HELP_LANGUAGES, LANGUAGES_DICT)
from django.db.models import Q
from frontend.forms import CreateAccountForm, UserMessageForm
from registration.backends import get_backend
from frontend.models import UserProfile, Tags

# find this in lib/python/site-packages/profiles
from profiles import views as profile_views

import django.contrib.auth.views
import os
import re
import datetime
import urllib
import itertools
import json
import random


from utilities import location


def frontpage(request, public_profile_field=None):
    user = request.user
    data = {
            'tags': Tags.sorted(),
            'language': 'python'
           }
    return render_to_response('frontend/homepage.html', data, context_instance=RequestContext(request))


def profile_detail(request, username):
    # The templates for this view are in templates/profiles/
    user = request.user
    profiled_user = get_object_or_404(User, username=username)
    profile = profiled_user.get_profile()

    extra_context = {
                     'owned_code_objects' : profile.owned_code_objects(user),
                     'emailer_code_objects' : profile.emailer_code_objects(username, user)
                    }
    return profile_views.profile_detail(request, username=username, extra_context=extra_context)

def redirect_dashboard_to_profile(request):
    user = request.user
    if not user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))
    return HttpResponseRedirect(reverse('profile',
                                kwargs=dict(username=user.username)))


def user_message(request, username):
    """
        This is a view to return a form ready for the user to send an
        email message to another user on the site.
    """
    form = UserMessageForm(data=request.POST or None)
    receiving_user = get_object_or_404(User, username=username)
    if request.method == "POST" and form.is_valid():
        #  send email
        from django.template.loader import render_to_string
        from django.conf import settings
        from django.core.mail import EmailMultiAlternatives

        sending_user_profile = get_object_or_404(UserProfile, user=request.user)
        receiving_user_profile = get_object_or_404(UserProfile, user=receiving_user)

        subject = "New message from %s" % sending_user_profile.display_name()
        body = form.cleaned_data['body']

        site = Site.objects.get_current()
        reply_url = "https://%s%s#message" % (site.domain,reverse("profile",kwargs={"username":sending_user_profile.user.username}))
        sender_profile_url = "https://%s%s" % (site.domain,reverse("profile",kwargs={"username":sending_user_profile.user.username}))
        if sending_user_profile.messages and receiving_user_profile.messages:
            text_content = render_to_string('emails/new_message.txt', locals(), context_instance=RequestContext(request) )
            html_content = render_to_string('emails/new_message.html', locals(), context_instance=RequestContext(request) )

            msg = EmailMultiAlternatives(subject, text_content, settings.FEEDBACK_EMAIL, [receiving_user_profile.user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)
        else:
            return HttpResponse('{"status" : "fail", "error" : "Both you and the recipient must allow messages"}')

        return HttpResponse('{"status" : "ok"}')

    elif request.method == "POST":
        return HttpResponse('{"status" : "fail", "error" : "Please fill in the message"}')

    return render_to_response('profiles/message.html', {'form':form, 'profile' : receiving_user}, context_instance = RequestContext(request))

def edit_profile(request):
    form = UserProfileForm()
    return profile_views.edit_profile(request, form_class=form)

def process_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('frontpage'))

def login(request):
    error_messages = []

    #grab the redirect URL if set
    redirect = request.GET.get('next') or request.POST.get('redirect', '')

    # Get invitation token
    token = request.GET.get('t', None)

    #Create login and registration forms
    login_form = SigninForm()
    registration_form = CreateAccountForm()

    if request.method == 'POST':
        #Existing user is logging in
        if request.POST.has_key('submit'):

            login_form = SigninForm(data=request.POST)
            if login_form.is_valid():
                user = auth.authenticate(username=request.POST['user_or_email'], password=request.POST['password'])

                #Log in
                auth.login(request, user)

                #set session timeout
                if request.POST.has_key('remember_me'):
                    request.session.set_expiry(settings.SESSION_TIMEOUT)

                if redirect:
                    return HttpResponseRedirect(redirect)
                else:
                    return HttpResponseRedirect(reverse('profile',
                                                kwargs=dict(username=request.user.username)))

        #New user is registering
        elif request.POST.has_key('register'):

            registration_form = CreateAccountForm(data=request.POST)

            if registration_form.is_valid():
                backend = get_backend(settings.REGISTRATION_BACKEND)
                new_user = backend.register(request, **registration_form.cleaned_data)


                #sign straight in
                signed_in_user = auth.authenticate(username=request.POST['username'], password=request.POST['password1'])
                auth.login(request, signed_in_user)

                #redirect
                if redirect:
                    return HttpResponseRedirect(redirect)
                else:
                    return HttpResponseRedirect(reverse('profile',
                                                kwargs=dict(username=request.user.username)))

    context = {'registration_form': registration_form,
               'login_form': login_form,
               'error_messages': error_messages,
               'redirect': redirect,
               }

    return render_to_response('registration/extended_login.html',
      context, context_instance = RequestContext(request))



def help(request, mode=None, language=None):
    tutorials = {}
    viewtutorials = {}
    if not language:
        language = "python"
    display_language = LANGUAGES_DICT[language]
    other_languages = [ (l, d) for (l, d) in HELP_LANGUAGES if l != language]

    if mode=="code_documentation": # Support legacy URL.
        mode="documentation"

    context = { 'mode' : mode, 'language' : language, 'display_language' : display_language,
             'tutorials': tutorials, 'viewtutorials': viewtutorials,
             'other_languages' : other_languages }

    if not mode or mode=="intro":
        mode = "intro"
        context["include_tag"] = "frontend/help_intro.html"
        context["mode"] = "intro"
    elif mode=="faq":
        mode = "faq"
        context["include_tag"] = "frontend/help_faq.html"
        context["mode"] = "faq"
    elif mode=="tutorials":
        # new ordering by the number at start of title, which we then strip out for display
        if language == "python":
            tutorials[language] = Scraper.objects.filter(privacy_status="public", istutorial=True, language=language).order_by('title')
            for scraper in tutorials[language]:
                scraper.title = re.sub("^[\d ]+", "", scraper.title)
        else:
            tutorials[language] = Scraper.objects.filter(privacy_status="public", istutorial=True, language=language).order_by('created_at')
        viewtutorials[language] = View.objects.filter(privacy_status="public", istutorial=True, language=language).order_by('created_at')
        context["include_tag"] = "frontend/help_tutorials.html"

    else:
        context["include_tag"] = "frontend/help_%s_%s.html" % (mode, language)

    return render_to_response('frontend/help.html', context, context_instance = RequestContext(request))

def browse_wiki_type(request, wiki_type=None, page_number=1):
    special_filter = request.GET.get('filter', None)
    ff = request.GET.get('forked_from', None)
    return browse(request, page_number, wiki_type, special_filter,ff)

def browse(request, page_number=1, wiki_type=None, special_filter=None, ff=None):
    all_code_objects = scraper_search_query(request.user, None).select_related('owner','owner__userprofile_set')

    if wiki_type:
        all_code_objects = all_code_objects.filter(wiki_type=wiki_type)

    # One last check because this is a slightly convoluted way of building this page.
    if not ff:
        ff = request.GET.get('forked_from', None)

    if ff:
        try:
            s = Scraper.objects.get(short_name=ff)
            if s and not s.privacy_status == 'private' and not s.privacy_status == 'deleted':
                all_code_objects = all_code_objects.filter(forked_from=s)
        except Scraper.DoesNotExist:
            # Just ignore the forked_from if the scraper does not exist
            pass

    #extra filters (broken scraper lists etc)
    if special_filter == 'sick':
        all_code_objects = all_code_objects.filter(status='sick')
    elif special_filter == 'no_description':
        all_code_objects = all_code_objects.filter(description='')
    elif special_filter == 'no_tags':
        #hack to get scrapers with no tags (tags don't recognise inheritance)
        if wiki_type == 'scraper':
            all_code_objects = TaggedItem.objects.get_no_tags(Scraper.objects.exclude(privacy_status="deleted").order_by('-created_at') )
        else:
            all_code_objects = TaggedItem.objects.get_no_tags(View.objects.exclude(privacy_status="deleted").order_by('-created_at') )


    # filter out scrapers that have no records unless we are looking at the forked_from list
    if not ff and not special_filter:
        all_code_objects = all_code_objects.exclude(wiki_type='scraper', scraper__record_count=0)

    form = SearchForm()

    dictionary = { "ff": ff, "scrapers": all_code_objects, 'wiki_type':wiki_type, "form": form, 'special_filter': special_filter, 'language': 'python'}
    return render_to_response('frontend/browse.html', dictionary, context_instance=RequestContext(request))


def search_urls(request, partial):
    """
    When we search we want to handle anything that looks like a url and search for it within the
    codewiki.DomainScrape. This isn't mapped to a URL at the moment, it is expected that it will
    only be called from the search view.

    This does not take account of private scrapers that you do have access to, instead showing
    only public and protected scrapers, for now.
    """
    from codewiki.models import DomainScrape
    from urlparse import urlparse
    from django.db.models import Q

    url = urlparse(partial)
    q = Q(scraper_run_event__scraper__privacy_status__in=['public','protected'])
    q = q & (Q(domain__istartswith='http://%s' % (url.netloc,)) | Q(domain__istartswith='https://%s' % (url.netloc,)))
    dsqs = DomainScrape.objects.filter(q).distinct('scraper_run_event__scraper')

    ctx = {
        'form'     : SearchForm(initial={'q': partial}),
        'scrapers_num_results'    : dsqs.count(),
        'scrapers' : [ d.scraper_run_event.scraper for d in dsqs.all().distinct() ],
    }

    # TODO: We need a template for url search results
    return render_to_response('frontend/search_url_results.html', ctx, context_instance = RequestContext(request))



def search(request, q=""):
    if (q != ""):
        form = SearchForm(initial={'q': q})
        q = q.strip()

        # If q looks like a url then we should just pass it through to search_urls
        # and return that instead.
        if re.match('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', q):
            return search_urls(request,q)

        tags = Tag.objects.filter(name__icontains=q)
        scrapers = scraper_search_query(request.user, q)

        # The following line used to exclude private scrapers, but these were already excluded in
        # the call to scraper_search_query above.
        scrapers = scrapers.exclude(usercoderole__role='email')
        scrapers_num_results = tags.count() + scrapers.count()

        users = user_search_query(request.user, q)
        users_num_results = users.count()

        return render_to_response('frontend/search_results.html',
            {
                'scrapers': scrapers,
                'users': users,
                'tags': tags,
                'scrapers_num_results': scrapers_num_results,
                'users_num_results': users_num_results,
                'form': form,
                'query': q},
            context_instance=RequestContext(request))

    # If the form has been submitted, or we have a search term in the URL
    # - redirect to nice URL
    elif (request.POST):
        form = SearchForm(request.POST)
        if form.is_valid():
            q = form.cleaned_data['q']
            # Process the data in form.cleaned_data
            # Redirect after POST
            return HttpResponseRedirect('/search/%s/' % urllib.quote(q.encode('utf-8')))
        else:
            form = SearchForm()
            return render_to_response('frontend/search_results.html', {'form': form},
                context_instance=RequestContext(request))
    else:
        form = SearchForm()
        return render_to_response('frontend/search_results.html', {'form': form}, context_instance = RequestContext(request))


@login_required
def stats(request):
    return render_to_response('frontend/stats.html', {}, context_instance=RequestContext(request))


def tags(request):
    all_tags = {}

    # Python 2.7 would clean this up by using collections.Counter
    def update_tags(tag):
        existing = all_tags.get(tag.name, None)
        if existing:
            existing.count += tag.count
        else:
            all_tags[tag.name] = tag

    scraper_tags = Tag.objects.usage_for_model(Scraper, counts=True,
      filters={'privacy_status':'public'})
    view_tags = Tag.objects.usage_for_model(View, counts=True,
      filters={'privacy_status':'public'})
    for tag in itertools.chain(scraper_tags, view_tags):
        update_tags(tag)

    tags = calculate_cloud(all_tags.values(),
      steps=4, distribution=LOGARITHMIC)

    return render_to_response('frontend/tags.html', {'tags':tags},
      context_instance=RequestContext(request))

def tag(request, tag):
    ttag = get_tag(tag)
    code_objects = None

    if ttag:
        # query set of code objects this user can see
        user_visible_code_objects = scraper_search_query(request.user, None)

        # inlining of tagging.models.get_by_model() but removing the content_type_id condition so that tags
        # attached to scrapers and views get interpreted as tags on code objects
        code_objects = user_visible_code_objects.extra(
            tables=['tagging_taggeditem'],
            where=['tagging_taggeditem.tag_id = %s', 'codewiki_code.id = tagging_taggeditem.object_id'],
            params=[ttag.pk])

    return render_to_response('frontend/tag.html', {'tag_string': tag, 'tag' : ttag, 'scrapers': code_objects}, context_instance=RequestContext(request))

def resend_activation_email(request):
    form = ResendActivationEmailForm(request.POST or None)

    template = 'frontend/resend_activation_email.html'
    if form.is_valid():
        template = 'frontend/resend_activation_complete.html'
        try:
            user = User.objects.get(email=form.cleaned_data['email_address'])
            if not user.is_active:
                site = Site.objects.get_current()
                user.registrationprofile_set.get().send_activation_email(site)
        except Exception, ex:
            print ex

    return render_to_response(template, {'form': form}, context_instance = RequestContext(request))



def user_profile_from_account_code(account_code):
    """From the account_code, created in *subscribe()* (above), extract the user id,
    and then the UserProfile object, which is returned.
    """

    id = int(account_code.split('-')[0])
    user = User.objects.get(id=id)
    return user.get_profile()




def test_error(request):
    raise Exception('failed in test_error')

