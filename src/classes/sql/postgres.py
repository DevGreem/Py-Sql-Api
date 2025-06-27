from psycopg2 import connect
from psycopg2.extensions import connection, cursor
from typing import List, Dict, Any, Tuple, overload, Optional
from src.classes.sql.common.SQLClasses import *
from src.classes.sql.types import Row, Data
from src.types.params import ListOrTuple, EncryptValues
from itertools import chain

class Postgres():
    
    _connection: connection
    
    def __init__(
        self,
        *,
        config: Optional[DbConfig] = None,
        user: str = '',
        password: str = '',
        database: str = 'postgres',
        server: str = 'localhost',
        port: int = 5432,
        encrypt: EncryptValues = 'allow'
    ):
        
        if config:
            database = config.database
            user = config.uid
            password = config.pwd
            encrypt = config.encrypt
        
        self._connection = connect(
            dbname=database,
            user=user,
            password=password,
            host=server,
            port=port,
            sslmode=encrypt
        )
    
    @staticmethod
    def _serialize_rows(cursor: cursor) -> List[Dict]:
        
        if cursor.description is None:
            return [{}]
        
        column_names = [
            column[0]
            for column in cursor.description
        ]

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
    def _dump_schematic_object(schematic_object: SchematicObject) -> str:
        
        return f"{f'{schematic_object.sql_schema}.' if schematic_object.sql_schema else ''}{schematic_object.name}"
    
    def execute(self, query: str, vars: ListOrTuple = ()) -> cursor:
        
        db_cursor = self._connection.cursor()

        db_cursor.execute(query, vars)
            
        return db_cursor
    
    def fetch(self, query: str, vars: ListOrTuple = ()) -> List[Row]:
        
        cursor = self.execute(query, vars)
        
        try:
            return cursor.fetchall() if cursor.description else []
        finally:
            cursor.close()
    
    def tables(self, schema: SchemaBody = SchemaBody()) -> List[Row]:
        
        return self.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE';
        """, (schema.sql_schema,))
    
    def columns(self, query: ColumnsQuery) -> List[Dict[str, str]]:
        
        all_columns = self.fetch(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
            """,
            (query.table.sql_schema, query.table.name)
        )
        
        return [
            {
                "name": str(column[0]),
                "type": str(column[1])
            }
            for column in all_columns
        ]
        
    def select(self, query: SelectQuery) -> Data:
        
        params = []
        
        select_columns: str = '*'
        
        if query.columns:
            select_columns = ', '.join(self._dump_columns(query.columns))
        
        select_join: str = ''
        
        if query.join:
            get_join = lambda join: join.Get()
            
            select_join = ' '.join(list(map(get_join, query.join)))
        
        request: str = f"""
        SELECT {select_columns}
        FROM {self._dump_schematic_object(query.table)} {query.table.subname or ''}
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
            jump_rows = f'offset {query.offset.max_row}' if query.offset.max_row else ''
            
            request += f' LIMIT {query.offset.min_row} {jump_rows}'
        
        request.replace('None', 'null')
        
        request += ';'
        
        cursor = self.execute(request, params)
        
        answer = self._serialize_rows(cursor)
        
        return answer
    
    def insert(self, query: InsertQuery) -> List[Row]:
        
        table_columns: str = ''
        
        if query.columns:
            
            columns = ', '.join(query.columns)
            
            table_columns = f'({columns})'
        
        output_query: str = ''
        
        if query.output:
            output_columns = ', '.join(self._dump_columns(query.output))
            
            output_query = f'RETURNING {output_columns}'
        
        value_query: str = ', '.join(
            f'({", ".join("%s" for _ in range(len(new_row)))})'
            for new_row in query.values
        )
        
        request = f"""
        INSERT INTO {self._dump_schematic_object(query.table)} {table_columns}
        VALUES {value_query}
        {output_query};
        """
        
        answer = self.fetch(request, list(chain(*query.values)))
        
        return answer
    
    def update(self, query: UpdateQuery) -> List[Row]:
        
        set_text = ', '.join(
            f"{key} = %s"
            for key in query.column_values.keys()
        )
        
        return_columns = [column.name for column in query.output]
        
        params = [*query.column_values.values(), *return_columns]
        
        joined_conditions = f' WHERE {self._wheres_to_text(query.where, params)}' if query.where else ''
        
        return_query = f'RETURNING {", ".join(return_columns)}' if return_columns else ''
        
        request = f"""
        UPDATE {self._dump_schematic_object(query.table)}
        SET {set_text}
        {joined_conditions}
        {return_columns};
        """
        
        return self.fetch(request, params)
    
    def delete(self, query: DeleteQuery) -> List[Row]:
        
        params = []
        
        joined_conditions = f" WHERE {self._wheres_to_text(query.conditions, params)}" if query.conditions else ''
        
        return self.fetch(f"DELETE FROM {self._dump_schematic_object(query.table)} {joined_conditions};", params)
    
    def call(self, query: ExecQuery):
        
        params_values = ', '.join(f'{key} => %s' for key in query.params.keys()) if query.params else ''
        
        self.fetch(
            f"""
            CALL {self._dump_schematic_object(query.procedure)}({params_values});
            """,
            list(query.params.values())
        )
    
    def perform(self, query: FuncQuery) -> List[Row]:
        
        params_values = ', '.join(f'{key} => %s' for key in query.params.keys()) if query.params else ''
        
        return self.fetch(
            f"""
            PERFORM {self._dump_schematic_object(query.func)}({params_values});
            """,
            list(query.params.values())
        )