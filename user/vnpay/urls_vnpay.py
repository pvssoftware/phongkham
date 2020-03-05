from django.conf.urls import url

import user.vnpay.views_vnpay

urlpatterns = [
    url(r'^$', user.vnpay.views_vnpay.index, name='index'),
    url(r'^payment$', user.vnpay.views_vnpay.payment, name='payment'),
    url(r'^payment_ipn$', user.vnpay.views_vnpay.payment_ipn, name='payment_ipn'),
    url(r'^payment_return$', user.vnpay.views_vnpay.payment_return, name='payment_return'),
    url(r'^query$', user.vnpay.views_vnpay.query, name='query'),
    url(r'^refund$', user.vnpay.views_vnpay.refund, name='refund'),

]