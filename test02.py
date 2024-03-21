
from databases import Database
import asyncio

DATABASE_URL = "postgresql+asyncpg://u5637io3rv1pcb:pafa287c5bde9bf58245a880a8b0dcb44ddb0ae3090bb45f13bd066717907ffb1@c6b7lkfdshud3i.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d7n1a98iat38pm"

database = Database(DATABASE_URL)

async def print_connection_status():
    print("Is Database connected:", database.is_connected)

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

async def execute(): 
    await database.connect()
    await print_connection_status()

    query = f"INSERT INTO disease_tb (id, disease, treat) VALUES (3, 'Sana', '{treat}')"
    await database.execute(query=query)
    result = await database.fetch_all("select * from users")
    print(r for r in result)
    await database.disconnect()
    await print_connection_status()


# To run an asynchronous function, you need to await it.
async def run_execute():
    await execute()

# To execute the asynchronous function, you need to use an event loop.
asyncio.run(run_execute())


















# cn = sqlite3.connect("cocoa-ml.db")


# treat = '''
# La maladie du cacao Sana est une maladie fongique qui affecte les feuilles et les tiges des plants de cacao. Elle est causée par le champignon Colletotrichum gloeosporioides et se caractérise par la formation de taches brunes sur les feuilles et les tiges. Ces taches peuvent se propager rapidement et entraîner la mort des plants.

# Il existe plusieurs traitements possibles pour la maladie du cacao Sana. Le traitement le plus efficace est lutilisation dun fongicide. Les fongicides les plus couramment utilisés contre la maladie du cacao Sana sont les suivants :

# Mancozèbe

# Chlorothalonil

# Dithane M-45

# Il est important de noter que lutilisation de fongicides peut être nocive pour lenvironnement. Il est donc important de suivre les instructions du fabricant lors de lapplication des fongicides.

# En plus de lutilisation de fongicides, il existe dautres mesures qui peuvent être prises pour prévenir et contrôler la maladie du cacao Sana. Ces mesures comprennent :

# La plantation de plants sains
# Lélimination des plants malades
# La rotation des cultures
# Lutilisation dengrais équilibrés
# La maladie du cacao Sana est une maladie grave qui peut entraîner des pertes de rendement importantes. Il est important de prendre des mesures pour prévenir et contrôler cette maladie afin de protéger les cultures de cacao.
# '''

# treat = str(treat)

# # query = f"INSERT INTO treatments_tb VALUES (3, 'Fitoftora', 'trhr');"
# query = f"UPDATE treatments_tb SET name = 'Monilia' WHERE id =2"

# # async def dbexc():
# #     await database.connect()
# #     await database.execute(query=query)
# #     await database.disconnect()
# # dbexc()
# cn.cursor()
# cn.execute(query)
# cn.commit()
# cn.close()
# 

