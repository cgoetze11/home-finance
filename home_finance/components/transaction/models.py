import datetime
import json
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
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    date = models.DateTimeField()
    num = models.CharField(max_length=10, null=True, help_text='Used to record check numbers')
    notes = models.CharField(max_length=200, blank=True, null=True)
    transfer_account = models.ForeignKey(external_account.ExternalAccount, on_delete=models.DO_NOTHING,
                                         null=True, related_name='transfer_acct')
    reconciled = models.BooleanField(default=False)
    ''' A transaction with no category means it should have children transactions--so it represents a split.
        In this case, the amount is the summary amount of the splits, so it represents the entire transaction amount.
    '''
    category = models.ForeignKey(category.Category, null=True, on_delete=models.DO_NOTHING)


def load_from_file(to_account: external_account.ExternalAccount, file_name: str):
    """
    Load transactions from a file into a specific ExternalAccount

    The format of the is expected to be JSON and be a list of transactions with each transaction having fields like:
    { "amount": -61.5,
      "category": "Misc",
      "cleared": "X",
      "date": "1999-10-23",
      "memo": null,
      "num": null,
      "payee": "ATM Withdrawal 210 RAILROAD AVE",
      "splits": [
      {
        "amount": -61.0,
        "category": null,
        "memo": null,
        "percent": null,
        "to_account": "dummy2"
      },
      {
        "amount": -0.5,
        "category": "Bank Charges",
        "memo": null,
        "percent": null,
        "to_account": null
      }],
      "to_account": null
    }
    """
    with open(file_name) as f:
        txns = json.load(f)
        for txn in txns:
            splits = []
            new_txn = createTransaction(to_account, txn)
            for split in txn['splits']:
                splits.append(createTransactionFromSplit(new_txn, split))
            new_txn.save()
            for split in splits:
                split.parent = new_txn
            Transaction.objects.bulk_create(splits)


def findTransactions(to_account: external_account.ExternalAccount, data: dict):
    """
    Find possible matching transactions, but include new possible transaction in case it doesn't match
    """
    candidate = createTransaction(to_account, data)
    if candidate.num:
        possible_filter = Transaction.objects.filter(amount=candidate.amount,
                                                     num=candidate.num,
                                                     account=to_account)
    else:
        possible_filter = Transaction.objects.filter(amount=candidate.amount,
                                                     date__gt=candidate.date - datetime.timedelta(days=7),
                                                     date__lt=candidate.date + datetime.timedelta(days=7),
                                                     account=to_account)
    return candidate, possible_filter.all()

def createTransaction(to_account: external_account.ExternalAccount, data: dict):
    """
    Create a top level transaction, ignoring the splits
    """
    cat = _getUnique(category.Category, data.get('category'))
    acct = _getUnique(external_account.ExternalAccount, data.get('to_account'))
    desc = data['payee'] if 'payee' in data and data.get('payee') else data.get('memo')
    if desc is None:
        if acct:
            desc = f'Transfer {"to" if data["amount"] < 0 else "from"} {acct.name}'
        else:
            desc = ''

    cleared = True if ('cleared' in data and data.get('cleared')) else False
    return Transaction(amount=data['amount'],
                       parent=None,
                       account=to_account,
                       description=desc,
                       date=datetime.datetime.strptime(f'{data["date"]}-12:00-+0800', '%Y-%m-%d-%H:%M-%z'),
                       num=data.get('num'),
                       notes=data.get('memo'),
                       reconciled=cleared,
                       category=cat,
                       transfer_account=acct)



def _getUnique(cls, name: str):
    """
    Get a unique model from the supplied name. Returns None if no matching item was found
    """
    if name:
        items = cls.objects.filter(name=name).all()
        if items:
            return items[0]

def createTransactionFromSplit(parent_txn: Transaction, data: dict):
    """
    Create a transaction in memory from the supplied dictionary representing a split

    We do look-ups on Category and external accounts
    """
    transfer_acct = None
    cat = None
    if 'to_account' in data and data.get('to_account'):
        transfer_acct = _getUnique(external_account.ExternalAccount, data['to_account'])
        if not transfer_acct:
            raise Exception(f'Failed to find referenced external account: {data["to_account"]}')
    if 'category' in data and data.get('category'):
        cat = _getUnique(category.Category, data['category'])
        if not cat:
            raise Exception(f'Failed to find referenced category: {data["category"]}')
    desc = None
    if 'memo' in data and data.get('memo'):
        desc = data['memo']
    elif 'category' in data and data.get('category'):
        desc = data['category']
    elif 'to_account' in data and data.get('to_account'):
        desc = data['to_account']
    else:
        desc = ''
    notes = data.get('memo')
    return Transaction(amount=data.get('amount'),
                       description=desc,
                       notes=notes,
                       category=cat,
                       date=parent_txn.date,
                       account=parent_txn.account,
                       transfer_account=transfer_acct)
