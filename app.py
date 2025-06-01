from fastapi import FastAPI, status, Query, Request, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from classes.database import Database
from classes.SQLClasses import Table, SelectQuery, InsertQuery, UpdateQuery, DeleteQuery, ColumnsQuery, ExecQuery
from typing import Any, Annotated
from functions.dependencies import db_params
from pydantic import BaseModel

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
def Execute(command: str, request: Request):
    
    db: Database = Database()
    
    return db.execute(command).fetchall()

@app.get('/tables')
def Tables() -> Table:
    db: Database = Database()

    return db.tables()

@app.get('/columns/{entity_name}')
def Columns(entity_name: str, types: bool = Query(False)) -> list[str] | list[dict[str, str]]:
    db: Database = Database()
    
    return db.columns(entity_name, types)

#region POST

@app.post('/columns')
def ColumnsBody(query: ColumnsQuery = Body(...)) -> list[str] | list[dict[str, str]]:
    
    db: Database = Database()
    
    answer = db.columns_class(query)
    
    return answer

@app.post('/select')
def BodySelect(query: SelectQuery = Body(...)) -> list[dict[str, Any]]:
    
    db: Database = Database()
    
    answer = db.select(query)
    
    return answer

@app.post('/select/{entity}')
def Select(entity: str, query: SelectQuery = Body(SelectQuery(table=None))) -> list[dict[str, Any]]:
    
    query.table = Table(name=entity, subname=None)
    
    return BodySelect(query)

@app.post('/insert')
def BodyInsert(query: InsertQuery = Body(...)):
    
    db: Database = Database()
    
    answer = db.insert(query)
    
    try:
        return answer.fetchall()
    except:
        pass

@app.post('/exec')
def ExecClass(query: ExecQuery = Body(...)):
    
    db: Database = Database()
    
    response = db.procedure_class(query)
    
    try:
        return response.fetchall()
    except:
        pass

@app.post('/exec/{procedure}')
def Exec(procedure: str, params: dict[str, Any] = Body(...)):
    
    db: Database = Database()
    
    return db.procedure(procedure, params)

#region PUT

@app.put('/update', status_code=status.HTTP_204_NO_CONTENT)
def Update(query: UpdateQuery):
    
    db: Database = Database()
    
    db.update(query)

#region DELETE

@app.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
def Delete(query: DeleteQuery):
    
    db: Database = Database()
    
    db.delete(query)