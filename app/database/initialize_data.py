from pony.orm import db_session
from .models import Card
import csv


@db_session
def populate_card_table():
    if Card.select().count() > 0:
        print("Los datos de cartas ya estan en la base de datos. No se realizará la inicialización")
        return
    cartas = 'app/resources/cartas.csv'
    with open(cartas, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        for row in csvreader:
            number, card_type, name, description = row
            Card(number=number, type=card_type,
                 name=name, description=description)
