import json

from pydantic import BaseModel, RootModel, StrictStr, StrictInt, StrictBool

from app.core.config import settings


class KnowledgeBaseDocument(BaseModel):
    Type: StrictStr
    Filepath: StrictStr
    Size: StrictInt
    Loaded: StrictBool


class KnowledgeBase(RootModel):
    root: dict[str, KnowledgeBaseDocument]

    @classmethod
    def load(cls, file_path: str = None) -> "KnowledgeBase":
        if not file_path:
            file_path = settings.KNOWLEDGE_BASE_FILEPATH
        with open(file_path, "r") as f:
            data = json.load(f)
            return cls.model_validate(data)

    def dump(self, file_path: str = None) -> str:
        if not file_path:
            file_path = settings.KNOWLEDGE_BASE_FILEPATH
        with open(file_path, "w") as f:
            json.dump(self.model_dump(), f, indent=4)
        return json.dumps(self.model_dump(), indent=4)

    def add(self, key: str, attribute: KnowledgeBaseDocument):
        self.root[key] = attribute
        self.dump()

    def update(self, key: str, attribute: KnowledgeBaseDocument):
        if key in self.root:
            self.root[key] = attribute
            self.dump()
        else:
            raise KeyError(f"No attribute found with key: {key}")

    def remove(self, key: str):
        self.root.pop(key)
        self.dump()
