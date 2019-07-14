from sqlalchemy.orm import aliased

from fares.models import Trip

onward_trip = aliased(Trip)
return_trip = aliased(Trip)
