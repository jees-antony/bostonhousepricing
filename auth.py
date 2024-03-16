import bcrypt
import jwt
from database import database

# Secret key to sign JWT token
SECRET_KEY = "mysecretkey"

# Function to verify username and password against SQLite database
async def authenticate_user(username: str, password: str):

    result = await database.fetch_one("SELECT password FROM users WHERE username = '{username}'")
    # Fetch hashed password from the database for the given username

    if result:
        # Verify the password against the stored hash
        hashed_password = result[0]
        print(result[0])
        pass_enc = password.encode('utf-8')
        
        print(hashed_password)
        if bcrypt.checkpw(pass_enc, hashed_password):
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
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password

# Function to save user data to the SQLite database
async def save_user(username: str, password: str):

    # Hash the password before storing it in the database
    hashed_password = hash_password(password)
    hashed_password = await database.fetch_one("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))