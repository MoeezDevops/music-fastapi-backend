from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import TEXT, VARCHAR, Column, LargeBinary, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import uuid
import bcrypt

app = FastAPI()
                            # user   passwordofdb     port   dbname
DATABASE_URL = 'postgresql://postgres:qwerty@localhost:5432/fluttermusicapp'

# Creating the SQLAlchemy engine to connect to the database.
# This connects to the PostgreSQL database using the DATABASE_URL.
engine = create_engine(DATABASE_URL)

# SessionLocal is a factory function that creates new session objects. 
# It binds the session to the engine and controls how transactions are committed.
# It uses `autocommit=False` which means that the session will not automatically commit
# transactions. You have to explicitly call `db.commit()` to persist changes to the database.
# It also uses `autoflush=False`, meaning the session will not automatically flush changes
# to the database before each query. This gives you control over when to flush.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create an instance of the session to interact with the database.
# This session object will be used for queries and database transactions.
db = SessionLocal()

# Pydantic model to handle user input data in the signup request
# The BaseModel helps validate the incoming data, ensuring it matches the expected structure.
class UserCreate(BaseModel):
    name: str
    email: str              # pydantic user to get body in response of HTTP
    password: str

# The base class for SQLAlchemy models. This will be used to create a User model.
Base = declarative_base()

# SQLAlchemy model for the 'users' table in the database.
# This defines the structure of the 'users' table and how it maps to a Python object.
class User(Base):
    __tablename__ = 'users'

    # Define the columns for the 'users' table in the database.
    id = Column(TEXT, primary_key=True)  # User ID (primary key)
    name = Column(VARCHAR(100))          # User's name (string of up to 100 characters)
    email = Column(VARCHAR(100))         # User's email (string of up to 100 characters)
    password = Column(LargeBinary)       # User's password (hashed, stored as binary data)

# Endpoint to handle user signup
@app.post('/signup')
def sign_up(user: UserCreate):
    #TODO
    # Extract the data coming from the request body (this will be validated by Pydantic)
    print(user.name)
    print(user.email)
    print(user.password)

    # Check if the user already exists in the database by email.
    # Query the database to find if any existing user has the same email.
    user_DB = db.query(User).filter(User.email == user.email).first()
    
    if user_DB:
        # If user already exists, raise a 400 HTTP exception with an error message.
        raise HTTPException(400, 'User with the same email already exists!')
    
    # Hash the password using bcrypt to ensure it's securely stored.
    # bcrypt is used to generate a hash of the password, which is stored in the database
    # instead of the plaintext password for better security.
    hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt(16))

    # Create a new user record. Generate a UUID for the user ID and assign the hashed password.
    user_DB = User(id=str(uuid.uuid4()), email=user.email, password=hashed_pw, name=user.name)
    
    # Add the new user to the session. This doesn’t commit the changes yet.
    db.add(user_DB)
    
    # Commit the transaction to save the new user in the database.
    db.commit()

    # Refresh the session to reflect any changes made to the object (e.g., the ID after commit).
    db.refresh(user_DB)

    # Return the newly created user as a response.
    return user_DB

# Create all tables in the database. This ensures that if the 'users' table doesn’t exist yet,
# it will be created.
Base.metadata.create_all(engine)  # This creates the 'users' table if it doesn't exist.
