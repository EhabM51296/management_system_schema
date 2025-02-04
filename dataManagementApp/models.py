from django.db import models

class SchemaData(models.Model):
    table_name = models.CharField(max_length=255, unique=True)
    fields = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)