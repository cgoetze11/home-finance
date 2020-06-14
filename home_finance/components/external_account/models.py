from django.db import models


class ExternalAccount(models.Model):
    """
    Model definition for an ExternalAccount.
    """
    PATELCO = 'patelco'

    ALLOWED_ACCOUNTS = [
        (PATELCO, 'Patelco')
    ]   

    name = models.CharField(max_length=100, choices=ALLOWED_ACCOUNTS)
    description = models.CharField(max_length=100)
    interest_rate = models.FloatField(blank=True, null=True)
    notes = models.CharField(max_length=200, blank=True, null=True)
