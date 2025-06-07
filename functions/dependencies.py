from fastapi import Depends, Query
from typing import Annotated
from classes.SQLClasses import DbConfig

def get_db_params(
    server: str = Query(..., description='Database Server'),
    database: str = Query(..., description='Database Name'),
    uid: str = Query(..., description='User Name'),
    pwd: str = Query(..., description='User Password'),
    encrypt: str = Query("no", description='Data encryptation')
) -> DbConfig:
    
    return DbConfig(
        server=server,
        database=database,
        uid=uid,
        pwd=pwd,
        encrypt=encrypt
    )