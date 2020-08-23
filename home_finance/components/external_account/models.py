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

def create(name, description, interest=None, notes=None):
    externalAccount = ExternalAccount(name=name, description=description, interest_rate=interest, notes=notes)
    externalAccount.save()
