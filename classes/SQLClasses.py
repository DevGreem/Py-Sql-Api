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

class Table(SQLObject):
    subname: str|None = None

class Column(SQLObject):
    type: str|None = None
    table: str|None = None

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
    
    first_table: Table
    first_table_column: Column
    second_table_column: Column
    comparation: str = '='

class Join(BaseModel):
    
    table: Table
    on: On|None = None
    type: str = 'inner' #? Inner join, left join, right join, outer join
    
    def Get(self) -> str:
        return f"""{self.type} join {self.table.name} {self.table.subname}
            on {self.on.first_table.subname}.{self.on.first_table_column.name} {self.on.comparation} {self.table.subname}.{self.on.second_table_column.name}
            """

class SelectQuery(BaseModel):
    table: Table|None = None
    join: list[Join]|None = None
    columns: list[Column]|None = None
    where: list[Where]|None = None
    order_by: Order_By|None = None
    having: list[Having]|None = None
    group_by: Group_By|None = None

class InsertQuery(BaseModel):
    table: Table
    columns: list[str]|None = None
    values: list[Any]

class UpdateQuery(BaseModel):
    table: Table
    column_values: dict[str, Any]
    where: list[Where]|None = None

class DeleteQuery(BaseModel):
    table: Table
    conditions: list[Where]|None = None

class ColumnsQuery(BaseModel):
    table: str
    return_columns_types: bool = False
    joins: list[str]|None = None