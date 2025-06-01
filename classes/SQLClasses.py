from pydantic import BaseModel
from typing import TypedDict
from typing import Any

class DbConfig(BaseModel):
    
    server: str
    database: str
    uid: str
    pwd: str
    encrypt: str

class SQLObject(BaseModel):
    name: str

class SchematicObject(SQLObject):
    sql_schema: str = 'dbo'

class Table(SchematicObject):
    subname: str|None = None
    columns: tuple[str, ...]|None = None

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
    table: Table|None = None
    join: list[Join]|None = None
    columns: list[Column]|None = None
    where: list[Where]|None = None
    order_by: Order_By|None = None
    having: list[Having]|None = None
    group_by: Group_By|None = None
    offset: Offset|None = None

class InsertQuery(BaseModel):
    table: Table
    columns: list[str]|None = None
    values: list[Any]
    output: list[Column]|None = None

class UpdateQuery(BaseModel):
    table: Table
    column_values: dict[str, Any]
    where: list[Where]|None = None

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
    conditions: list[Where]|None = None

class ColumnsQuery(BaseModel):
    table: str
    return_columns_types: bool = False
    joins: list[str]|None = None

class ExecQuery(BaseModel):
    procedure: Procedure
    params: dict[str, Any]|None = None