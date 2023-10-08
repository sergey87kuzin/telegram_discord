import urllib

from django.conf import settings


def create_prodamus_order_object(order):
    order_string = f"?order_id={order.id}&products[0][price]={order.total_cost}" \
                   "&products[0][quantity]=1&products[0][name]=Обучающие материалы&do=link"
    return order_string
