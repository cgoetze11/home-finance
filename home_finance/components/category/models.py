from django.db import models

class Category(models.Model):
    """
    Model definition for a Category.
    """ 

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, null=True, blank=True, related_name='subcategories')
