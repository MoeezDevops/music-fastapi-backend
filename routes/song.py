import uuid
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session
from database import get_db
from middleware.auth_middleware import auth_middleware
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from models.fav_model import Favourite
from models.songModel import SongModel
from pydantic_schema.favourite import favourite
from sqlalchemy.orm import joinedload

router = APIRouter()
# Configuration       
cloudinary.config( 
    cloud_name = "dixzr0mye", 
    api_key = "451335636374767", 
    api_secret = "KAtGfl5OVtocce4r8dsVLEJnrVI", # Click 'View API Keys' above to copy your API secret
    secure=True
)

@router.post('/upload',status_code=201)
# #FFFFFF color save format
def upload_song(song: UploadFile = File(...) , 
                thumbnail : UploadFile = File(...),
                artist: str = Form(...),
                song_name: str = Form(...),
                hex_code: str = Form(...),
                db: Session = Depends(get_db),
                auth_dict = Depends(auth_middleware)):
    songs_id = str(uuid.uuid4())
    song_res = cloudinary.uploader.upload(song.file , resource_type='auto', folder =f'song/{songs_id}')
    print(song_res)
    
    thumbnail_res = cloudinary.uploader.upload(thumbnail.file , resource_type='image', folder =f'song/{songs_id}')
    print(thumbnail_res['url'])
    
    new_song = SongModel(
        id=songs_id,
        song_url=song_res['url'],
        thumbnail_url = thumbnail_res['url'],
        artist = artist,
        hex_codes= hex_code,
        song_name= song_name
    )
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    print(f'new songs    kwpodkwqposowqkspoq     {new_song.hex_codes}')
    return new_song


@router.get('/list')
def getList(db:Session = Depends(get_db),auth_dict = Depends(auth_middleware)):
    song_db =db.query(SongModel).all()
    print(song_db)
    return song_db

@router.post('/favourite')
def favourite_song(song:favourite,db: Session=Depends(get_db),
                   auth_details = Depends(auth_middleware)):
    # song is already favourite by the user
    users_id = auth_details['uid']
    fav_song= db.query(Favourite).filter(Favourite.song_id == song.fav_id,Favourite.user_id == users_id).first()
    if fav_song:
        db.delete(fav_song)
        db.commit()
        return {'message': False}
    else:
        new_fav = Favourite(id =str(uuid.uuid4()),song_id=song.fav_id,user_id=users_id)
        db.add(new_fav)
        db.commit()
        return{'message': True}
    # if the song is already fav, unfav it
    # if unfav, fav
    pass

@router.get('/list/favourite')
def getFavList(db:Session = Depends(get_db),auth_dict = Depends(auth_middleware)):
    user_id = auth_dict['uid']
    fav_song= db.query(Favourite).filter(Favourite.user_id == user_id).options(
        joinedload(Favourite.song),
        joinedload(Favourite.user),
    ).all()
    print(fav_song)
    return fav_song