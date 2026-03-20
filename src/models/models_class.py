from pydantic import BaseModel


class ReaderModel(BaseModel):
    files: dict[str, str]


class ParserModel(BaseModel):
    args: list[str]
