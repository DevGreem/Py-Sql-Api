import pyodbc
from pyodbc import Connection, Cursor, connect
from typing import Any, List, Dict
from src.classes.sql.common.SQLClasses import *
from src.types.params import ListOrTuple
from src.classes.sql.types import Data, ProcedureParams

class Database():

    _connection: Connection

    def __init__(self, config: DbConfig, driver: str, autocommit: bool = True):
        
        self._connection = connect(
            f'DRIVER={driver};'
            f'SERVER={config.server};'
            f'DATABASE={config.database};'
            f'UID={config.uid};'
            f'PWD={config.pwd};'
            f'Encrypt={config.encrypt};'
            f'TrustServerCertificate=true;'
            'Connection Timeout=60;',
            autocommit=autocommit
        )
    
    @staticmethod
    def _serialize_rows(cursor: Cursor) -> List[Dict]:
        column_names = [column[0] for column in cursor.description]

        result = [dict(zip(column_names, row)) for row in cursor.fetchall()]

        return result
    
    def _where_to_text(self, where: Where) -> str:
        return f"{where.to_column.name} {where.comparation} ?"
    
    def _wheres_to_text(self, wheres: List[Where]|List[Having], params: List[Any]) -> str:
        
        text: str = ''
        
        cantity = len(wheres)
            
        for i in range(cantity):
            where = wheres[i]
            
            text += f" {self._where_to_text(where)} {where.joiner if i < cantity-1 else ''}"
            params.append(where.value)
        
        return text
    
    @staticmethod
    def _dump_column(column: Column) -> str:
        
        as_column: str = ''
        
        if column.rename:
            as_column: str = f'as {column.rename}'
        
        return f'{column.name} {as_column}'
    
    def _dump_columns(self, columns: List[Column]):
        
        new_columns = list(map(lambda column: self._dump_column(column), columns))
        
        return new_columns
    
    @staticmethod
    def _dump_table(table: Table) -> str:
        
        return f"{f'{table.sql_schema}.' if table.sql_schema else ''}{table.name}" 

    def commit(self):
        self._connection.commit()

    def execute(self, query: str, *params: list[Any]|tuple[Any]) -> Cursor:
        cursor = self._connection.execute(query, *params)

        return cursor
    
    def tables(self) -> list[str]: ...
    
    def columns(self, query: ColumnsQuery) -> List[Dict[str, str]]: ...
    
    def select(self, query: SelectQuery) -> Data: ...
    
    def insert(self, query: InsertQuery) -> Cursor: ...
    
    def update(self, query: UpdateQuery) -> Cursor: ...
    
    def delete(self, query: DeleteQuery) -> Cursor: ...
    
    def procedure(self, query: ExecQuery) -> Cursor: ...