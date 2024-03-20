from databases import Database

# DATABASE_URL = "postgresql://your_username:your_password@your_host:your_port/your_database"
DATABASE_URL = "postgresql+asyncpg://u5637io3rv1pcb:pafa287c5bde9bf58245a880a8b0dcb44ddb0ae3090bb45f13bd066717907ffb1@c6b7lkfdshud3i.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d7n1a98iat38pm"

# database = Database("sqlite:///cocoa-ml.db")
database = Database(DATABASE_URL)
