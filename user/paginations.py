from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    page_size = 5 
    page_size_query_param = 'page'
    max_page_size = 1000

class HistoryPagination(PageNumberPagination):
    page_size = 5 
    page_size_query_param = 'page'
    max_page_size = 1000
 
