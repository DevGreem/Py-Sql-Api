import re
from re import Match
from typing import Any, Union, Pattern, Literal

class SqlConvertor():
    
    @staticmethod
    def convert_to_sql_value(value: Union[Any, str]) -> tuple[str, Literal[True]]|tuple[Any, Literal[False]]:
        
        lower_value = value.strip().lower()
        
        try:
            return bool(lower_value), False
        except:
            return lower_value, True
    
    @staticmethod
    def to_sql_value(value: Any) -> str|Any:
        
        if not isinstance(value, str):

            if isinstance(value, bool):
                return int(value)
            
            return value
        
        return repr(value)
    
    @staticmethod
    def match_sql_value(value: Match) -> str|int|bool:
        
        getted_value = value.group(1)
        
        if not isinstance(getted_value, str):
            
            if isinstance(getted_value, bool):
                return int(getted_value)
            
            return getted_value
        
        return repr(getted_value)
    
    @staticmethod
    def to_column_value(query: str) -> str|None:
        
        pattern = r'(\d+)\s+(\d{1,7})\s+(\d+)'