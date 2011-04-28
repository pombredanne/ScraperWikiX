from django.template import RequestContext, TemplateDoesNotExist
from django.shortcuts import render_to_response
from django.http import Http404
from codewiki.models import Code
import os
import re
import codewiki
import settings

def titleize(title):
    """ Turns 'some_slug' into 'Some Slug' """
    if title:
        return ' '.join( [ x.capitalize() for x in title.split('_') ])
    return ''

def docmain(request, language=None, path=None):
#    language = request.GET.get('language', None) or request.session.get('language', 'python')
    if language is None:
        language = request.session.get('language', 'python')
    request.session['language'] = language
    context = {'language':language }
    
    context["title"] = titleize(path)
    if path:
        context["docpage"] = 'documentation/includes/%s.html' % re.sub("\.\.", "", path)  # remove attempts to climb into another directory
        if not os.path.exists(os.path.join(settings.SCRAPERWIKI_DIR, "templates", context["docpage"])):
            raise Http404
    return render_to_response('documentation/docbase.html', context, context_instance=RequestContext(request))


    # should also filter, say, on isstartup=True and on privacy_status=visible to limit what can be injected into here
def contrib(request, short_name):
    context = { }
    try:
        scraper = codewiki.models.Code.objects.filter(language="html").get(short_name=short_name) 
    except Code.DoesNotExist:
        raise Http404
    if not scraper.actionauthorized(request.user, "readcode"):
        raise Http404
    
    context["doccontents"] = scraper.get_vcs_status(-1)["code"]
    context["title"] = scraper.title
    context["scraper"] = scraper
    return render_to_response('documentation/docbase.html', context, context_instance=RequestContext(request))

def docexternal(request):
    return render_to_response('documentation/apibase.html', { }, context_instance=RequestContext(request))



