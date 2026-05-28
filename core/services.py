from django.core.paginator import Paginator

from team_finder.constants import ITEMS_PER_PAGE


def get_page(queryset, page_number, per_page=ITEMS_PER_PAGE):
    """Return a Page object for the given queryset and page number."""
    return Paginator(queryset, per_page).get_page(page_number)
