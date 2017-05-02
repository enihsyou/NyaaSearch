from itertools import chain

from django.core.paginator import Paginator
from django.db.models import ForeignKey
from django.http import JsonResponse
from .models import *


def model_to_dict(instance):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if not getattr(f, 'editable', False):
            continue
        if isinstance(f, ForeignKey):
            data[f.name] = str(f.rel.to.objects.get(pk=f.value_from_object(instance)))
            continue
        data[f.name] = f.value_from_object(instance)
    return data


def detail(request, sukebei=False):
    error_message = []
    error_code = 0
    query_name = request.GET.get('q', '')
    database = 'sukebei' if sukebei else 'default'
    try:
        page_point = int(request.GET.get('page', 1))
    except ValueError:
        page_point = 1
        error_message.append('error in parsing \'page_point\'')
        error_code = 1
    try:
        page_size = int(request.GET.get('page_size', 10))
    except ValueError:
        page_size = 10
        error_message.append('error in parsing \'page_size\'')
        error_code = 1

    page = Paginator([], page_size)
    result_size = 0
    results = []
    if query_name and not error_code:
        database_query = Torrents.objects.using(database).filter(torrent_name__contains=query_name)
        result_size = len(database_query)
        page = Paginator(database_query, page_size)
        if page.num_pages >= page_point:
            page_result = page.page(page_point)
            for i in page_result:
                results.append(model_to_dict(i))
        else:
            error_code = 1
            error_message.append('empty page')
    json_response = JsonResponse(
        {
            'query': query_name,
            'result_size': result_size,
            'current_page': page_point,
            'page_size': page_size,
            'page_counts': page.num_pages,
            'results': results,
            'status_code': error_code,
            'status_message': error_message,
        },
        json_dumps_params={'ensure_ascii': False, 'indent': 2})
    json_response['Access-Control-Allow-Origin'] = '*'
    return json_response
