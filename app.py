from fastapi import FastAPI, status, Query, Request, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.classes.sql.common.database import Database
from src.classes.sql.postgres import Postgres
from src.classes.sql.common.SQLClasses import SchemaBody, SelectQuery, InsertQuery, UpdateQuery, DeleteQuery, ColumnsQuery, ExecQuery, DbConfig, FuncQuery
from typing import Any, Annotated, List, Dict
from src.functions import get_db_params
from pydantic import BaseModel
from pyodbc import Cursor
from src.classes.sql.types import Row, Data

# TODO: Cambiar la api para que funcione con la nueva libreria

app: FastAPI = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

#region GET

@app.get("/")
def Get():
    return { "Hello": "World" }

@app.get('/execute/{command}')
def Execute(command: str, params: DbConfig = Depends(get_db_params)):
    
    db = Postgres(config=params)
    
    answer = db.fetch(command)
    
    return answer

@app.post('/tables')
def Tables(schema: SchemaBody = Body(..., description='Tables Schema'), params: DbConfig = Depends(get_db_params)) -> List[Row]:
    db = Postgres(config=params)

    return db.tables(schema)

#region POST

@app.post('/columns')
def ColumnsBody(
    query: ColumnsQuery = Body(...),
    params: DbConfig = Depends(get_db_params)
) -> List[str] | List[Dict[str, str]]:
    
    db = Postgres(config=params)
    
    answer = db.columns(query)
    
    return answer

@app.post('/select')
def BodySelect(
    query: SelectQuery = Body(...),
    params: DbConfig = Depends(get_db_params)
) -> Data:
    
    db = Postgres(config=params)
    
    answer = db.select(query)
    
    return answer

@app.post('/insert')
def BodyInsert(query: InsertQuery = Body(...), params: DbConfig = Depends(get_db_params)) -> List[Row]:
    
    db = Postgres(config=params)
    
    answer = db.insert(query)
    
    return answer

@app.post('/call')
def ExecClass(query: ExecQuery = Body(...), params: DbConfig = Depends(get_db_params)):
    
    db = Postgres(config=params)
    
    db.call(query)

@app.post('/perform')
def Perform(query: FuncQuery = Body(...), params: DbConfig = Depends(get_db_params)) -> List[Row]:
    
    db = Postgres(config=params)
    
    answer = db.perform(query)
    
    return answer

#region PUT

@app.put('/update')
def Update(query: UpdateQuery = Body(...), params: DbConfig = Depends(get_db_params)) -> List[Row]:
    
    db = Postgres(config=params)
    
    answer = db.update(query)
    
    return answer

#region DELETE

@app.delete('/delete')
def Delete(query: DeleteQuery, params: DbConfig = Depends(get_db_params)) -> List[Row]:
    
    db = Postgres(config=params)
    
    answer = db.delete(query)
    
    return answer