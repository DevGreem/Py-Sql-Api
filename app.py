from fastapi import FastAPI, status, Query, Request, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from classes.database import Database
from classes.SQLClasses import Table, SelectQuery, InsertQuery, UpdateQuery, DeleteQuery, ColumnsQuery
from typing import Any, Annotated
from functions.dependencies import db_params
from pydantic import BaseModel

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
def Execute(command: str, params: Annotated[dict, Depends(db_params)]):
    db: Database = Database(params)
    
    return db.execute().fetchall()

@app.get('/tables')
def Tables(params: Annotated[dict, Depends(db_params)]):
    db: Database = Database(params)

    return db.tables()

@app.get('/columns/{entity_name}')
def Columns(entity_name: str, params: Annotated[dict, Depends(db_params)], types: bool = Query(False)) -> list[str] | list[dict[str, str]]:
    db: Database = Database(params)
    
    return db.columns(entity_name, types)

#region POST

@app.post('/columns')
def ColumnsBody(params: Annotated[dict, Depends(db_params)], query: ColumnsQuery = Body(...)):
    
    db: Database = Database(params)
    
    answer = db.columns_class(query)
    
    return answer

@app.post('/select')
def BodySelect(params: Annotated[dict, Depends(db_params)], query: SelectQuery = Body(...)):
    
    db: Database = Database(params)
    
    answer = db.select(query)
    
    return answer

@app.post('/select/{entity}')
def Select(params: Annotated[dict, Depends(db_params)], entity: str, query: SelectQuery = Body(SelectQuery(table=None))):
    
    query.table = Table(name=entity, subname=None)
    
    return BodySelect(query)

@app.post('/insert', status_code=status.HTTP_204_NO_CONTENT)
def BodyInsert(params: Annotated[dict, Depends(db_params)], query: InsertQuery = Body(...)):
    
    db: Database = Database(params)
    
    db.insert(query)

@app.post('/exec/{procedure}', status_code=status.HTTP_204_NO_CONTENT)
def Exec(procedure: str, params: Annotated[dict, Depends(db_params)], procedure_params: dict[str, Any] = Body(...)):
    
    db: Database = Database(params)
    
    return db.procedure(procedure, procedure_params)

#region PUT

@app.put('/update', status_code=status.HTTP_204_NO_CONTENT)
def Update(params: Annotated[dict, Depends(db_params)], query: UpdateQuery):
    
    db: Database = Database(params)
    
    db.update(query)

#region DELETE

@app.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
def Delete(params: Annotated[dict, Depends(db_params)], query: DeleteQuery):
    
    db: Database = Database(params)
    
    db.delete(query)