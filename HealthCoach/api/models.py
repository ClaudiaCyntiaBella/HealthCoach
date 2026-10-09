"""Model database nutrisi akan dikelola pada bagian Backend & Database."""

from django.db import models


class Nutrition(models.Model):
    id = models.BigIntegerField(primary_key=True)
    calories = models.FloatField()
    proteins = models.FloatField()
    fat = models.FloatField()
    carbohydrate = models.FloatField()
    name = models.CharField(max_length=255)
    image = models.URLField(max_length=1000, blank=True, default="")
    name_normalized = models.CharField(max_length=255, db_index=True)

    class Meta:
        db_table = "nutrition"
        ordering = ["id"]

    def __str__(self):
        return self.name
