from typing import NewType, Literal, Annotated, Any, List, Tuple, Dict

Engine = Literal['postgres', 'sqlserver']

ListOrTuple = List[Any]|Tuple[Any, ...]

EncryptValues = Literal['disable', 'allow', 'prefer', 'require', 'verify-full']