from datetime import datetime
import json
from django.db.models import Sum
from django.db.models.manager import Manager
from .util import moneyfmt
from home_finance.components.category.models import Category
from home_finance.components.external_account.models import ExternalAccount
from home_finance.components.transaction.models import Transaction, findTransactions

def current_balance(account: ExternalAccount):
    print(f'Current balance on account {account.name} is:\t\t\t\t {current_account_balance(account)}')

def load_transactions(to_account: ExternalAccount, filename: str):
    """
    Interactively walk through each provided transaction and help the user decide on the action to take.
    """
    with open(filename) as f:
        transactions = json.load(f)

    print(f'Found {len(transactions)} in the file: {filename}')
    # tell user the balance after before we start
    print(f'Starting balance on account {to_account.name} is:\t\t\t\t {current_account_balance(to_account)}')

    for txn in transactions:
        (candidate, possibles) = findTransactions(to_account, txn)
        if len(possibles) > 0:
            print(f'Possible matches of: {candidate.date:%Y-%m-%d(%a)}: {candidate.amount}, {candidate.description}')
            for i, possible in enumerate(possibles):
                print(f'\t{i}: {possible.date:%Y-%m-%d(%a)}: {possible.amount}, {possible.description}\n'
                      f'\t\tCategory: {possible.category.name if possible.category else "None"},'
                      f'\t\tTransfer account: {possible.transfer_account.name if possible.transfer_account else "None"},'
                      f'\t\tReconciled: {possible.reconciled}')
            if len(possibles) == 1 and possibles[0].reconciled:
                print(f'Above transaction was found and is reconciled, so no action being provided.')
            else:
                handled = False
                while not handled:
                    prompt_input = input(f'If this transaction appears above and you are happy with it, input "s".'
                                         f'To reconcile a transaction from the list type: "r<num>".')
                    if prompt_input.startswith('s'):
                        print(f'Skipping transaction: {candidate.date:%Y-%m-%d(%a)}: {candidate.amount}, {candidate.description}')
                        handled = True
                    if prompt_input.startswith('r'):
                        transaction_index = int(prompt_input[1:])
                        if transaction_index < 0 or transaction_index >= len(possibles):
                            print(f'Cannot reconcile item number: {transaction_index} since it is outside of the range')
                        else:
                            possibles[transaction_index].reconciled = True
                            possibles[transaction_index].save()
                            print(f'Reconciled transaction.')
                            handled = True
        else:
            print(f'No matching transactions found. {candidate.date:%Y-%m-%d(%a)}: {candidate.amount}, {candidate.description}')
            add_new = input(f'Input "n" to create a new one or anything else to skip.')
            if add_new == 'n' or add_new == 'N':
                category, transfer_account = prompt_for_category_or_transfer_account()
                candidate.category = category
                candidate.transfer_account = transfer_account
                cleared = input(f'This transaction will be set as reconciled, type: "no" to change that.')
                candidate.reconciled = False if cleared.upper() == 'NO' else True
                new_description = input(f'Type a new description (or just enter to skip): {candidate.description}')
                if len(new_description) > 1:
                    candidate.description = new_description
                new_notes = input(f'Type notes to add, or enter to skip')
                if len(new_notes) > 1:
                    candidate.notes = new_notes
                candidate.save()
                print(f'New balance on account {candidate.account.name} is:\t\t\t\t {current_account_balance(candidate.account)}')
            else:
                print(f'Ignoring transaction')


def new_transaction(transaction_date: str, amount: float, description: str, notes: str = None,
                    account: ExternalAccount = None, category: Category = None, num: str = None):
    """
    Walk through creating a new transaction for a user.
    """
    fmt_sep = '-' if '-' in transaction_date else '/'
    t_date = datetime.strptime(f'{transaction_date}__12:00-+0800', f'%Y{fmt_sep}%m{fmt_sep}%d__%H:%M-%z')
    transaction = Transaction(date=t_date, amount=amount, description=description, notes=notes, num=num,
                              account=account, category=category)
    transfer_transaction = None
    if not account:
        transaction.account = prompt_for_account()
    if not category:
        transaction.category = prompt_for_category()
    # When creating a manual transaction, a transfer should appear in both accounts, but during import only one,
    # since it will be imported on each account individually
    transfer_account = prompt_for_account(is_transfer=True)
    if not notes:
        notes = input('Input any notes for this transaction: ')
    transaction.notes = notes
    if transfer_account:
        transaction.transfer_account = transfer_account
        transfer_transaction = Transaction(date=t_date, amount=-1.0*amount, description=description, notes=notes,
                                           account=transfer_account, transfer_account=transaction.account,
                                           category=transaction.category)
    transaction.save()
    if transfer_transaction:
        transfer_transaction.save()
    # tell user the balance after this transaction has been saved
    print(f'New balance on account {transaction.account.name} is:\t\t\t\t {current_account_balance(transaction.account)}')
        

def prompt_for_category_or_transfer_account():
    """
    Get input and help user find a category or transfer account to be used
    """
    category = prompt_for_category()
    transfer_account = prompt_for_account(is_transfer=True)
    return category, transfer_account


def prompt_for_category():
    """
    Prompt for an category
    """
    return prompt_by_name('category', Category.objects)


def prompt_for_account(is_transfer: bool = False):
    """
    Prompt for an account
    """
    acct = prompt_by_name(f'{"transfer " if is_transfer else ""}account', ExternalAccount.objects)
    if acct:
        current_balance(acct)
    return acct


def prompt_by_name(object_name: str, objects: Manager):
    """
    Prompt for an item by name
    """
    item = None
    handled = False
    while not handled:
        item_query = input(f'Input the name of an {object_name} to find, or "none" to skip {object_name} lookup: ')
        if item_query.upper() == 'NONE':
            handled = True
        else:
            possible_items = objects.filter(name__contains=item_query).all()
            for i, possible in enumerate(possible_items):
                print(f'\t{i}: {possible.name}')
            select_item = input(f'Which {object_name} number do you want to select, or "none" to skip: ')
            if select_item.upper() == 'NONE':
                handled = True
            else:
                try:
                    select_index = int(select_item)
                    if select_index < 0 or select_index > len(possible_items):
                        print(f'Input provided is out of range.')
                    else:
                        item = possible_items[select_index]
                        handled = True
                except ValueError:
                    print(f'Failed to parse input as an integer.')
    return item


def current_account_balance(account: ExternalAccount, as_string=True):
    """Get the current balance from the account as either a printable string or numeric
    TODO: support date argument to support ignoring future dates, so I can get today's current balance ignoring pending bills
    """
    balance = Transaction.objects.filter(account=account, parent__isnull=True).aggregate(Sum('amount')).get('amount__sum')
    if as_string:
        return moneyfmt(balance)
    else:
        return balance


def recent_transactions(account: ExternalAccount, count=10):
    """Print some of the most recent transactions from this account"""
    balance = current_account_balance(account, as_string=False)
    txns = Transaction.objects.filter(account=account).order_by('-date')[:count]
    for txn in txns:
        print(f'{txn.date:%Y-%m-%d(%a)}: {txn.num if txn.num else "    "} {moneyfmt(balance)} {txn.amount}, {txn.description}, {txn.notes}\n'
              f'\tCategory: {txn.category.name if txn.category else "None"},'
              f'\tTransfer account: {txn.transfer_account.name if txn.transfer_account else "None"},'
              f'\tReconciled: {txn.reconciled}')
        balance = balance - txn.amount
