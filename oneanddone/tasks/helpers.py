from jingo import register

@register.function
def page_url(request, page):
    query = request.GET.copy()
    query['page'] = page
    return ''.join(['?' , query.urlencode()])
