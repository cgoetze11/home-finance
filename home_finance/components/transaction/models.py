from django.db import models
from home_finance.components.external_account.models import ExternalAccount


class Transaction(models.Model):
    """
    Model definition for a Transaction.
    """

    account = models.ForeignKey(ExternalAccount, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subtransactions')
    description = models.CharField(max_length=200)
    amount = models.FloatField()
    date = models.DateTimeField()
    notes = models.CharField(max_length=200, blank=True, null=True)
    transfer = models.BooleanField(default=False)
    reconciled = models.BooleanField(default=False)
