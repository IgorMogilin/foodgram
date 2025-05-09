from rest_framework.pagination import PageNumberPagination

from .constants import PAGINATION_PAGE_SIZE


class PageLimitPagination(PageNumberPagination):
    """Кастомная пагинация с ограничением количества элементов на странице.
    По умолчанию выводит 6 элементов на страницу.
    Позволяет переопределять количество элементов через параметр 'limit'.
    Например: /api/recipes/?limit=10 вернет 10 элементов на странице.
    """

    page_size = PAGINATION_PAGE_SIZE
    page_size_query_param = "limit"
