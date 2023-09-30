from .db_factory import db
from .models import *
from .initialize_data import populate_card_table

db.generate_mapping(create_tables=True)

populate_card_table()
