from django.core.paginator import Paginator
from django.conf import settings


def get_paginators_page(posts, request):
    paginator = Paginator(posts, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
