import pyodbc
from pyodbc import Connection, Cursor, connect
import json
import re
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
    
    def _wheres_to_text(self, wheres: list[Where]|list[Having], params: list[Any]) -> str:
        
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
    
    def _dump_columns(self, columns: list[Column]):
        
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
    
    def tables(self) -> list[str]:
        
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
    
    def columns_class(self, query: ColumnsQuery) -> list[dict[str, str]]:
        
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
    
    def select(self, query: SelectQuery) -> list[dict[str, Any]]:
        
        params = []
        
        select_columns: str = '*'
        
        if query.columns:
            select_columns = ', '.join(self._dump_columns(query.columns))
        
        select_join: str = ''
        
        if query.join:
            get_join = lambda join: join.Get()
            
            select_join = ' '.join(list(map(get_join, query.join)))
        
        request: str = f"""select {select_columns}
            from {self._dump_table(query.table)} {query.table.subname or ''}
            {select_join}
            """
        
        if query.where:
            request += f' where {self._wheres_to_text(query.where, params)}'
        
        if query.order_by:
            order_methods = ['asc', 'desc']
            
            order_columns = ', '.join(self._dump_columns(query.order_by.columns))
            
            request += f' order by {order_columns} {order_methods[query.order_by.desc]}'
        
        if query.group_by:
            group_columns = ', '.join(self._dump_columns(query.group_by.columns))
            
            request += f' group by {group_columns}'
        
        if query.having:
            request += f' having {self._wheres_to_text(query.having, params)}'
        
        if query.offset:
            request += f" offset {query.offset.min_row} rows fetch next {query.offset.max_row} rows only"
        
        request.replace('None', 'null')
        
        print(request)
        print(params)
        
        cursor = self.execute(request, params)
        
        answer = self._serialize_rows(cursor)
        
        print(answer)
        
        return answer
    
    def insert(self, query: InsertQuery):
        
        table_columns = ''
        
        if query.columns:
            columns = ', '.join(query.columns)
            table_columns = f'({columns})'
        
        query_params = ', '.join('?' for _ in range(len(query.values)))
        
        output_query = ''
        
        if query.output:
            output_columns = ', '.join(self._dump_columns(query.output))
            output_query = f"OUTPUT {output_columns}"
        
        request = f"""insert into {self._dump_table(query.table)} {table_columns}
        {output_query}
        values ({query_params})"""
        
        print(request)
        print(query.values)
        
        return self.execute(request, query.values)
    
    def update(self, query: UpdateQuery):
        
        params = list(query.column_values.values())
        
        set_text = ', '.join(
            f"{key} = ?"
            for key in query.column_values.keys()
        )
        
        joined_conditions = f' where {self._wheres_to_text(query.where, params)}' if query.where else ''
        
        return self.execute(f"update {query.table.name} set {set_text} {joined_conditions}", params)
    
    def delete(self, query: DeleteQuery):
        
        params = []
        
        joined_conditions = f" where {self._wheres_to_text(query.conditions, params)}" if query.conditions else ''
        
        return self.execute(f"delete from {query.table.name} {joined_conditions}", params)
    
    def procedure(self, name: str, procedure_params: dict[str, Any]):

        params = list(procedure_params.values())
            
        sql_params: str = ', '.join(f"@{key} = ?" for key in procedure_params.keys())
            
        return self.execute(f"exec {name} {sql_params}", params)
    
    def procedure_class(self, query: ExecQuery):
        
        to_execute = f'''exec {f'{query.procedure.sql_schema}.' if query.procedure.sql_schema else ''}{query.procedure.name}
            {', '.join(f"@{key} = ?" for key in query.params.keys())}
        '''
        
        print(to_execute)
        print(query.params.values())
        
        return self.execute(
            to_execute,
            list(query.params.values())
        )