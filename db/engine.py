from django.conf import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sa_engine = create_engine(settings.DATABASE_URL)

Session = sessionmaker(bind=sa_engine)
