from src.classes.sql.common.database import Database
from src.classes.sql.common.SQLClasses import *
from src.classes.sql.types import Data

class SQLServer(Database):
    
    def __init__(self, config: DbConfig, autocommit: bool = True):
        super().__init__(
            config=config,
            driver="{ODBC Driver 17 for SQL Server}",
            autocommit=autocommit
        )
    
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
    
    def columns(self, query: ColumnsQuery) -> list[dict[str, str]]:
        
        cursor = self._connection.cursor()
        all_columns = []
        
        main_columns = cursor.columns(query.table.name)
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
    
    def select(self, query: SelectQuery) -> Data:
        
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
    
    def procedure(self, query: ExecQuery):
        
        to_execute = f'''exec {f'{query.procedure.sql_schema}.' if query.procedure.sql_schema else ''}{query.procedure.name}
            {', '.join(f"@{key} = ?" for key in query.params.keys())}
        '''
        
        print(to_execute)
        print(query.params.values())
        
        return self.execute(
            to_execute,
            list(query.params.values())
        )