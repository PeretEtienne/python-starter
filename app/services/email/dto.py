from dataclasses import dataclass
from typing import Optional


@dataclass
class EmailMessageData:
    receivers: list[str]
    subject: str
    data: Optional[dict[str, str | int]] = None
    tpl: Optional[str] = None
    html: Optional[str] = None
    cc: Optional[list[str]] = None
    bcc: Optional[list[str]] = None
