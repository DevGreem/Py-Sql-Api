from typing import Any

class Helper():
    
    @staticmethod
    def tryCatch(func) -> tuple[Any, bool]:
        
        try:
            return func(), True
        except:
            return None, False
        
    @staticmethod
    def forEachCatch(funcs: list) -> Any|None:
        
        for func in funcs:
            
            result, success = Helper.tryCatch(func)
            
            if success:
                return result
        
        return None