from funfactory.helpers import urlparams
from jingo import register


@register.function
def page_url(request, page):
    params = dict(request.GET)
    params['page'] = page
    return urlparams('', **params)
