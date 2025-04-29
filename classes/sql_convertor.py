import re
from re import *
from typing import Any, Union

class SqlConvertor():
    
    @staticmethod
    def convert_to_sql_value(value: Union[Any, str]) -> tuple[str, True]|tuple[Any, False]:
        
        lower_value = value.strip().lower()
        
        try:
            return bool(lower_value), False
        except:
            pass
    
    @staticmethod
    def to_sql_value(value: Any) -> str|Any:
        
        if not isinstance(value, str):

            if isinstance(value, bool):
                return int(value)
            
            return value
        
        return repr(value)
    
    @staticmethod
    def match_sql_value(value: Match) -> str:
        
        value = match.group(1)
        
        if not isinstance(value, str):
            
            if isinstance(value, bool):
                return int(value)
            
            return value
        
        return repr(value)
    
    @staticmethod
    def to_column_value(query: str) -> str:
        
        pattern: Pattern = r'(\d+)\s+(\d{1,7})\s+(\d+)'