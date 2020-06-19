from django.db import models
from home_finance.components.transaction.models import Transaction


class Category(models.Model):
    """
    Model definition for a Category.
    """ 

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subcategories')
    transactions = models.ManyToManyField(Transaction, blank=True, null=True)
