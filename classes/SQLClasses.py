from pydantic import BaseModel
from fastapi import Query
from typing import TypedDict, Annotated
from typing import Any

class DbConfig(BaseModel):
    
    server: Annotated[str, Query(...)]
    database: Annotated[str, Query(...)]
    uid: Annotated[str, Query(...)]
    pwd: Annotated[str, Query(...)]
    encrypt: Annotated[str, Query(...)]

class SQLObject(BaseModel):
    name: str

class SchematicObject(SQLObject):
    sql_schema: str = 'dbo'

class Table(SchematicObject):
    subname: str|None = None
    columns: tuple[str, ...] = ()

class Procedure(SchematicObject): pass

class Column(SQLObject):
    type: str|None = None
    table: Table|None = None
    rename: str|None = None

class SQLInstructor(BaseModel):
    to_column: Column

class Where(SQLInstructor):
    
    comparation: str = '='
    value: Any
    joiner: str = '' #? AND, OR
    
    def Get(self) -> str:
        
        return f'{self.to_column.name} {self.comparation} {self.value} {self.joiner} '

class Having(Where): pass

class Group_By(BaseModel):
    
    columns: list[Column]

class Order_By(Group_By):
    
    desc: bool = False #? False = 'ASC', True = 'DESC'

class On(BaseModel):
    
    table_column: Column
    other_table: Table
    other_table_column: Column
    comparation: str = '='

class Join(BaseModel):
    
    table: Table
    on: On
    type: str = 'inner' #? Inner join, left join, right join, full join
    
    def Get(self) -> str:
        return f""" {self.type} join {f'{self.table.sql_schema}.' if self.table.sql_schema else ''}{self.table.name} {self.table.subname}
            on {self.table.subname}.{self.on.table_column.name} {self.on.comparation} {self.on.other_table.name}.{self.on.other_table_column.name}
            """

class Offset(BaseModel):
    min_row: int
    max_row: int

class SelectQuery(BaseModel):
    table: Table
    join: list[Join] = []
    columns: list[Column] = []
    where: list[Where] = []
    order_by: Order_By|None = None
    having: list[Having] = []
    group_by: Group_By|None = None
    offset: Offset|None = None

class InsertQuery(BaseModel):
    table: Table
    columns: list[str] = []
    values: list[Any]
    output: list[Column] = []

class UpdateQuery(BaseModel):
    table: Table
    column_values: dict[str, Any]
    where: list[Where] = []

class EditQuery(BaseModel):
    table_name: str
    column_pk: str
    pk_value: Any
    table_columns: dict[
        str,
        tuple[
            Column,
            Any, # Value
            dict[str, Any]
        ]
    ]

class DeleteQuery(BaseModel):
    table: Table
    conditions: list[Where] = []

class ColumnsQuery(BaseModel):
    table: str
    return_columns_types: bool = False
    joins: list[str] = []

class ExecQuery(BaseModel):
    procedure: Procedure
    params: dict[str, Any] = {}