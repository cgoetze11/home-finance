from django.db import models
import home_finance.components.category.models as category
import home_finance.components.external_account.models as external_account


class Transaction(models.Model):
    """
    Model definition for a Transaction.
    """

    account = models.ForeignKey(external_account.ExternalAccount, on_delete=models.DO_NOTHING)
    parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True, related_name='subtransactions')
    description = models.CharField(max_length=200)
    amount = models.FloatField()
    date = models.DateTimeField()
    notes = models.CharField(max_length=200, blank=True, null=True)
    transfer_account = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True)
    reconciled = models.BooleanField(default=False)
    ''' A transaction with no category means it should have children transactions--so it represents a split.
        In this case, the amount is the summary amount of the splits, so it represents the entire transaction amount.
    '''
    category = models.ForeignKey(category.Category, null=True, on_delete=models.DO_NOTHING)
