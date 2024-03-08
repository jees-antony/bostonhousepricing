import sqlite3
from databases import Database

database = Database("sqlite:///cocoa-ml.db")

cn = sqlite3.connect("cocoa-ml.db")


treat = '''
La maladie du cacao Sana est une maladie fongique qui affecte les feuilles et les tiges des plants de cacao. Elle est causée par le champignon Colletotrichum gloeosporioides et se caractérise par la formation de taches brunes sur les feuilles et les tiges. Ces taches peuvent se propager rapidement et entraîner la mort des plants.

Il existe plusieurs traitements possibles pour la maladie du cacao Sana. Le traitement le plus efficace est lutilisation dun fongicide. Les fongicides les plus couramment utilisés contre la maladie du cacao Sana sont les suivants :

Mancozèbe

Chlorothalonil

Dithane M-45

Il est important de noter que lutilisation de fongicides peut être nocive pour lenvironnement. Il est donc important de suivre les instructions du fabricant lors de lapplication des fongicides.

En plus de lutilisation de fongicides, il existe dautres mesures qui peuvent être prises pour prévenir et contrôler la maladie du cacao Sana. Ces mesures comprennent :

La plantation de plants sains
Lélimination des plants malades
La rotation des cultures
Lutilisation dengrais équilibrés
La maladie du cacao Sana est une maladie grave qui peut entraîner des pertes de rendement importantes. Il est important de prendre des mesures pour prévenir et contrôler cette maladie afin de protéger les cultures de cacao.
'''

treat = str(treat)

# query = f"INSERT INTO treatments_tb VALUES (3, 'Fitoftora', 'trhr');"
query = f"UPDATE treatments_tb SET name = 'Sana', treat = '{treat}' WHERE id =3"

# async def dbexc():
#     await database.connect()
#     await database.execute(query=query)
#     await database.disconnect()
# dbexc()
cn.cursor()
cn.execute(query)
cn.commit()
cn.close()
# 

