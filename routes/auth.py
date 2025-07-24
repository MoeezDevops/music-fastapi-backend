import uuid
import bcrypt
from fastapi import  Depends, HTTPException, Header
from models.user import User
from pydantic_schema.user_create import UserCreate
from fastapi import APIRouter
from database import  get_db
from sqlalchemy.orm import Session
import jwt
from middleware.auth_middleware import auth_middleware
from pydantic_schema.user_login import UserLogin
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.post('/signup',status_code=201)
def sign_up(user:UserCreate,db: Session=Depends(get_db)):
    #TODO
    # extract the data thats coming from req
    print(user.name)
    print(user.email)
    print(user.password)

    # check if the user already exists in db
    user_DB = db.query(User).filter(User.email == user.email).first()
    
    if  user_DB:
        raise HTTPException(400,'User with the same email already exists!')
    
    hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt(16))
    # add the user to the db
    user_DB = User(id=str(uuid.uuid4()),email=user.email,password=hashed_pw,name=user.name)
    
    db.add(user_DB)
    db.commit()
    db.refresh(user_DB)

    return user_DB

@router.post('/login')
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    # check if the user with same email already exist
    user_db = db.query(User).filter(User.email == user.email).first()
    if not user_db:
        raise HTTPException(400,'User with this is not exits!')
    
    # password matching or not
    is_match= bcrypt.checkpw(user.password.encode(),user_db.password)
    
    if not is_match:
        raise HTTPException(400,'Incorrect password!')
    
    token = jwt.encode({"id":user_db.id},'password_key')
    print('mm')

    return {'token':token,'user':user_db}

@router.get('/')
def current_user_data(db: Session=Depends(get_db),
                      user_dict = Depends(auth_middleware)):
    user = db.query(User).filter(User.id == user_dict['uid']).options(joinedload(User.favorites)).first()
    if not user:
        raise HTTPException(404,'User not found')
    return user

    