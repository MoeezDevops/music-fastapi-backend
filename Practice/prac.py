from fastapi import FastAPI, Request
from pydantic import BaseModel
app = FastAPI()

class Test(BaseModel):
    name: str
    age: int

@app.post('/')
def test(t:Test,q:str): #if yoy pass any param as Test(baseModel )
    print(t)            #it will consider it body else it will consider it query   
    return 'hello world'
