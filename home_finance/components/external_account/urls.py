from django.conf.urls import url

from home_finance.components.external_account.views import index

urlpatterns = [
    url('', index, name='index'),
]