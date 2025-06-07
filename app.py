from fastapi import FastAPI, status, Query, Request, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from classes.database import Database
from classes.SQLClasses import Table, SelectQuery, InsertQuery, UpdateQuery, DeleteQuery, ColumnsQuery, ExecQuery, DbConfig
from typing import Any, Annotated, List
from functions.dependencies import get_db_params
from pydantic import BaseModel
from pyodbc import Cursor

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
    
    db: Database = Database(params)
    
    answer = db.execute(command)
    
    return answer.fetchall()

@app.get('/tables')
def Tables(params: DbConfig = Depends(get_db_params)) -> List[str]:
    db: Database = Database(params)

    return db.tables()

@app.get('/columns/{entity_name}')
def Columns(
    entity_name: str,
    types: bool = Query(False),
    params: DbConfig = Depends(get_db_params)
    ) -> list[str] | list[dict[str, str]]:
    
    db: Database = Database(params)
    
    return db.columns(entity_name, types)

#region POST

@app.post('/columns')
def ColumnsBody(query: ColumnsQuery = Body(...), params: DbConfig = Depends(get_db_params)) -> list[str] | list[dict[str, str]]:
    
    db: Database = Database(params)
    
    answer = db.columns_class(query)
    
    return answer

@app.post('/select')
def BodySelect(query: SelectQuery = Body(...), params: DbConfig = Depends(get_db_params)) -> list[dict[str, Any]]:
    
    db: Database = Database(params)
    
    answer = db.select(query)
    
    return answer

@app.post('/insert')
def BodyInsert(query: InsertQuery = Body(...), params: DbConfig = Depends(get_db_params)):
    
    db: Database = Database(params)
    
    answer = db.insert(query)
    
    return answer.fetchall()

@app.post('/exec')
def ExecClass(query: ExecQuery = Body(...), params: DbConfig = Depends(get_db_params)):
    
    db: Database = Database(params)
    
    response = db.procedure_class(query)
    
    return response.fetchall()

#region PUT

@app.put('/update', status_code=status.HTTP_204_NO_CONTENT)
def Update(query: UpdateQuery, params: DbConfig = Depends(get_db_params)):
    
    db: Database = Database(params)
    
    return db.update(query)

#region DELETE

@app.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
def Delete(query: DeleteQuery, params: DbConfig = Depends(get_db_params)):
    
    db: Database = Database(params)
    
    return db.delete(query)