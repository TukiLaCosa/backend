from .db_factory import db
from .models import *

db.generate_mapping(create_tables=True)