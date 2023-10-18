from pony.orm import db_session
from .models import Card
import csv
from app.config.config import settings


@db_session
def populate_card_table():
    if Card.select().count() > 0:
        return

    with open(settings.CARDS_CSV_FILE_PTAH, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        for row in csvreader:
            number, card_type, card_subtype, name, description = row
            Card(number=number, type=card_type, subtype=card_subtype,
                 name=name, description=description)
