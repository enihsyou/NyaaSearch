from itertools import chain

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import ForeignKey

from django.http import JsonResponse
from .models import *


def model_to_dict(instance, database):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if not getattr(f, 'editable', False):
            continue
        if isinstance(f, ForeignKey):
            try:
                data[f.name] = str(f.rel.to.objects.using(database).get(pk=f.value_from_object(instance)))
            except ObjectDoesNotExist:
                data[f.name] = None
            continue
        data[f.name] = f.value_from_object(instance)
    return data


def detail(request, sukebei=False):
    error_message = []
    error_code = 0
    query_name = request.GET.get('q', '')
    database = 'sukebei' if sukebei else 'nyaa'
    try:
        page_point = int(request.GET.get('page', 1))
    except ValueError:
        error_code = 1
        error_message.append('error in parsing \'page_point\'')
        page_point = 1
    if page_point <= 0:
        error_message.append('invalid \'page_point\':{}, reset to {}'.format(page_point, 1))
        page_point = 1

    try:
        page_size = int(request.GET.get('page_size', 10))
    except ValueError:
        error_code = 1
        error_message.append('error in parsing \'page_size\'')
        page_size = 10
    if page_size > 1000:
        error_message.append('too big \'page_size\':{}, reset to {}'.format(page_size, 1000))
        page_size = 1000
    elif page_size <= 0:
        error_message.append('invalid \'page_size\':{}, reset to {}'.format(page_size, 10))
        page_size = 10

    result_size = 0
    results = []
    if query_name and not error_code:
        database_query = Torrents.objects.using(database).filter(torrent_name__contains=query_name).order_by(
            'torrent_id').reverse()
        result_size = len(database_query)
        for i in database_query[(page_point - 1) * page_size:page_point * page_size]:
            results.append(model_to_dict(i, database))

    return JsonResponse(
        {
            'query': query_name,
            'result_size': result_size,
            'current_page': page_point,
            'page_size': page_size,
            'page_counts': result_size // page_size + 1,
            'results': results,
            'status_code': error_code,
            'status_message': error_message,
        },
        json_dumps_params={'ensure_ascii': False, 'indent': 2})
