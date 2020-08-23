import re
from django.db import models


class ExternalAccount(models.Model):
    """
    Model definition for an ExternalAccount.
    """
    PATELCO = 'patelco'

    ALLOWED_ACCOUNTS = [
        (PATELCO, 'Patelco')
    ]   

    name = models.CharField(max_length=100, choices=ALLOWED_ACCOUNTS, unique=True)
    description = models.CharField(max_length=100)
    interest_rate = models.FloatField(blank=True, null=True)
    notes = models.CharField(max_length=200, blank=True, null=True)

def create(name, description, interest=None, notes=None):
    externalAccount = ExternalAccount(name=name, description=description, interest_rate=interest, notes=notes)
    externalAccount.save()


def load_from_file(input_file):
    '''Consume a file to create some external accounts.

    The file format should be, one account per line, and look like:
       Name: <name of account>, <other ignored info>
    '''
    name_pattern = re.compile(r'Name: ([^,]+),')
    with open(input_file) as f:
        for line in f:
            match = name_pattern.search(line)
            if match:
                account_name = match.group(1)
                try:
                    create(account_name, account_name)
                except Exception as e:
                    print(f'Failed loading account: {account_name}: {e}')


