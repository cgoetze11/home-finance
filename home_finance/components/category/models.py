import re
from django.db import models

class Category(models.Model):
    """
    Model definition for a Category.
    """ 

    '''The name of the category. A name with a colon indicates it is nested and has a parent, however
    the entire full name is always stored. For example, the category Tax:Federal is a child of the category Tax.
    '''
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True, related_name='subcategories')


def create_from_file(file_name):
    """
    Create some Category entries from an input file

    The file expects one category per line and the format should be:
    <category name>:  <number>
    Note that the category name may contain a colon, in which case it is considered a nested category,
    and the method with ensure the parent is correctly created and linked to the child.
    """
    name_pattern = re.compile(r'(.*):\s+\d+')
    with open(file_name) as f:
        for line in f:
            match = name_pattern.match(line)
            if match:
                category_name = match.group(1)
                ancestor_lineage = None
                for parent_name in category_name.split(':'):
                    new_name = parent_name if ancestor_lineage is None else f'{ancestor_lineage.name}:{parent_name}'
                    parent_category = Category.objects.filter(name=new_name).all()
                    if not parent_category:
                        c = Category(name=new_name, parent=ancestor_lineage)
                        c.save()
                        ancestor_lineage = c
                    else:
                        ancestor_lineage = parent_category[0]
            else:
                print(f'Failed to extract category from line: <{line}>')

