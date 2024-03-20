import bcrypt
import jwt
from database import database

# Secret key to sign JWT token
SECRET_KEY = "mysecretkey"

# Function to verify username and password against SQLite database
async def authenticate_user(username: str, password: str):

    result = await database.fetch_one(f"SELECT password FROM users WHERE username = '{username}'")
    # Fetch hashed password from the database for the given username

    if result:
        # Verify the password against the stored hash
        hash_password1 = result[0]
        print(result[0])
        pass_enc = password.encode('utf-8')
        hash_password1 = hash_password1.encode('utf-8')
        
        print(hash_password1)
        if bcrypt.checkpw(pass_enc, hash_password1):
            print(bcrypt.checkpw(pass_enc, hash_password1))
            return True
    return False

# Function to create JWT token
def create_jwt_token(username: str):
    payload = {"sub": username}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# Function to hash passwords using bcrypt
def hash_password(password: str):
    # Hash the password using bcrypt
    pass_has = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return pass_has

# Function to save user data to the postgres database
async def save_user(username: str, password: str):

    # Hash the password before storing it in the database
    hashed_password = hash_password(password)
    hashed_password = hashed_password.decode('utf-8')

    # Use parameterized query to insert user data
    query = "INSERT INTO users (username, password) VALUES (:username, :password);"
    await database.execute(query, values={"username": username, "password": hashed_password})