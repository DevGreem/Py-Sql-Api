from fastapi import Depends, Query
from typing import Annotated
from src.classes.sql.common.SQLClasses import DbConfig, EngineConfig
from src.types.params import EncryptValues

def get_db_params(
    server: str = Query(..., description='Database Server'),
    database: str = Query(..., description='Database Name'),
    uid: str = Query(..., description='User Name'),
    pwd: str = Query(..., description='User Password'),
    encrypt: EncryptValues = Query('require', description='Data encryptation'),
) -> DbConfig:
    
    return DbConfig(
        server=server,
        database=database,
        uid=uid,
        pwd=pwd,
        encrypt=encrypt
    )