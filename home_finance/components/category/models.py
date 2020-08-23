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
