from django.db import models


class SearchRequest(models.Model):
    request_id = models.CharField(db_index=True)


class Itinerary(models.Model):
    request = models.ForeignKey(on_delete=models.CASCADE, db_index=True)
    returning = models.BooleanField(default=False)

class Flight(models.Model):
    order = models.SmallIntegerField()

    


