import pyodbc
from pyodbc import *
import json
import re
from re import *
from typing import Any
from classes.SQLClasses import *

class Database():

    _connection: Connection

    def __init__(self, config: DbConfig, autocommit: bool = True):
        
        self._connection = connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={config.server};'
            f'DATABASE={config.database};'
            f'UID={config.uid};'
            f'PWD={config.pwd};'
            f'Encrypt={config.encrypt};'
            'TrustServerCertificate=no;'
            'Connection Timeout=60;',
            autocommit=autocommit
        )
    
    @staticmethod
    def _serialize_rows(cursor: Cursor) -> list[dict]:
        column_names = [column[0] for column in cursor.description]

        result = [dict(zip(column_names, row)) for row in cursor.fetchall()]

        return result
    
    def _where_to_text(self, where: Where) -> str:
        return f"{where.to_column.name} {where.comparation} ?"
    
    def _wheres_to_text(self, wheres: list[Where], params: list[Any]) -> str:
        
        text: str = ''
        
        cantity = len(wheres)
            
        for i in range(cantity):
            where = wheres[i]
            
            text += f" {self._where_to_text(where)} {where.joiner if i < cantity-1 else ''}"
            params.append(where.value)
        
        return text

    def commit(self):
        self._connection.commit()

    def execute(self, query: str, *params: list[Any]|tuple[Any]) -> Cursor|None:
        cursor = self._connection.execute(query, *params)

        return cursor
    
    def tables(self):
        
        tables = [
            row['TABLE_NAME'] 
            for row in self._serialize_rows(
                self.execute(
                    "exec sp_tables @table_owner='dbo'"
                )
            )
        ]

        return tables
    
    def columns(self, table_name: str, with_types: bool = False, joins: list[Join] = []) -> list[str] | list[dict[str, str]]:
        
        cursor = self._connection.cursor()
        all_columns = []
        
        main_columns = cursor.columns(table_name)
        all_columns.extend(main_columns)
        
        if joins:
            for join in joins:
                join_columns = cursor.columns(join.table.name)
                all_columns.extend(join_columns)
        
        if with_types:
            
            columns = [
                {
                    "name": str(column[3]),
                    "type": str(column[5]).split()[0].lower()
                }
                for column in all_columns
            ]
            
            return columns
            
        columns = [str(column[3]) for column in all_columns]
        
        return columns
    
    def columns_class(self, query: ColumnsQuery) -> list[Column]:
        
        cursor = self._connection.cursor()
        all_columns = []
        
        main_columns = cursor.columns(query.table)
        all_columns.extend(main_columns)
        
        if query.joins:
            
            for join in query.joins:
                join_columns = cursor.columns(join)
                all_columns.extend(join_columns)
            
        if query.return_columns_types:
            
            columns = [
                {
                    "name": str(column[3]),
                    "type": str(column[5]).split()[0].lower(),
                    "table": str(column[2])
                }
                for column in all_columns
            ]
            
            return columns

        return [
            {
                "name": str(column[3]),
                "table": str(column[2])
            }
            for column in all_columns
        ]
    
    def select(self, query: SelectQuery):
        
        params = []
        
        request: str = f"""select {', '.join(list(map(lambda column: column.name, query.columns))) if query.columns else '*'} 
            from {query.table.name} {query.table.subname or ''}
            {' '.join(list(map(lambda join: join.Get(), query.join))) if query.join else ''}
            """
        
        if query.where:
            request += f' where {self._wheres_to_text(query.where, params)}'
        
        if query.order_by:
            order_clause = ', '.join(list(map(lambda column: column.name, query.order_by.columns)))
            
            request += f' order by {order_clause} ?'
            params.append('desc' if query.order_by.desc else 'asc')
        
        if query.group_by:
            group_clause = ', '.join(list(map(lambda column: column.name, query.group_by.columns)))
            
            request += f' group by {group_clause}'
        
        if query.having:
            request += f' having {self._wheres_to_text(query.having, params)}'
        
        request.replace('None', 'null')
        
        cursor = self.execute(request, params)
        
        answer = self._serialize_rows(cursor)
        
        return answer
    
    def insert(self, query: InsertQuery):
        
        clause = ', '.join(query.columns)
        
        table_columns = f'({clause})' if query.columns else ''
        
        query_params = ', '.join('?' for _ in range(len(query.values)))
        
        request = f"insert into {query.table.name} {table_columns} values ({query_params})"
        
        self.execute(request, query.values)
    
    def update(self, query: UpdateQuery):
        
        params = list(query.column_values.values())
        
        set_text = ', '.join(
            f"{key} = ?"
            for key in query.column_values.keys()
        )
        
        joined_conditions = f' where {self._wheres_to_text(query.where, params)}' if query.where else ''
        
        self.execute(f"update {query.table.name} set {set_text} {joined_conditions}", params)
    
    def delete(self, query: DeleteQuery):
        
        params = []
        
        joined_conditions = f" where {self._wheres_to_text(query.conditions, params)}" if query.conditions else ''
        
        self.execute(f"delete from {query.table.name} {joined_conditions}", params)
    
    def procedure(self, name: str, procedure_params: dict[str, Any]):

        params = list(procedure_params.values())
            
        sql_params: str = ', '.join(f"@{key} = ?" for key in procedure_params.keys())
            
        self.execute(f"exec sp_{name} {sql_params}", params)