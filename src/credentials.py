from dataclasses import dataclass
from typing import Optional

@dataclass
class Credentials:
    url: str
    username: str
    password: str

@dataclass
class NullableCredentials:
    url: Optional[str]
    username: Optional[str]
    password: Optional[str]
