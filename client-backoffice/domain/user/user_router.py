from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status

from models import User
from database import get_db
from domain.user import user_crud, user_schema
from domain.user.user_crud import get_mentor_list
from domain.user.user_crud import pwd_context

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = "3a6a54dbd17251738203ab4e2cfcaa5503ffed2400dbc5a2357620ca4a17fcc7"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")
router = APIRouter(
    prefix="/api/user",
)


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = user_crud.get_user(db, username=username)
        if user is None:
            raise credentials_exception
        return user

# 회원가입한 내용을 디비에 보내는 것까지 역할 
@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def user_create(_user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = user_crud.get_existing_user(db, user_create=_user_create)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="이미 존재하는 사용자입니다.")
    user_crud.create_user(db=db, user_create=_user_create)
    

@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):

    # check user and password
    user = user_crud.get_user(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # make access token
    data = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }


@router.get("/get_mentor_list")
def get_mentor(db: Session = Depends(get_db)):
    _mentor_list = get_mentor_list(db)
    return _mentor_list


@router.get("/get_user_status")
def get_mentor(db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    return current_user


# 세원
# from fastapi.responses import HTMLResponse
# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
# import logging
# import requests


# templates = Jinja2Templates(directory="templates")


# @app.get('/cities', response_class=HTMLResponse)
# def get_signup(request: Request):
#     # logging.basicConfig(level='DEBUG')
#     # logging.debug('start~0')
#     context = {}
#     rsCity = []
#     cnt = 0
#     db = []

#     headers = {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
#     for city in db:
#         strs = f"http://worldtimeapi.org/api/timezone/{city['timezone']}"

#         r = requests.get(strs, headers=headers)

#         cur_time = r.json()['datetime']
#         cnt += 1

#         rsCity.append( {"id": cnt, 'name': city['name'], 'timezone': city['timezone'], 'current_time': cur_time } )

#         # logging.debug(db)

#     context['request'] = request
#     context['rsCity'] = rsCity

#     return templates.TemplateResponse("city_list.html", context)