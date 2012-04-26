from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from recuro import recurly_parser

@csrf_exempt
def notify(request):
    obj = recurly_parser.parse(request.raw_post_data)
    obj.save()
    return HttpResponse("ok", mimetype="text/plain")