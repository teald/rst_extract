"""Code block with metadata about the original RST file."""

from typing import Optional

from pydantic import BaseModel, FilePath, StrictInt, StrictStr


class Block(BaseModel):
    code: list[StrictStr] = []
    offsets: dict[StrictStr, StrictInt] = {}
    path: Optional[FilePath] = None

    # RST-specific metadata
    directive: Optional[StrictStr] = None
    options: list[StrictStr] = []
