import json
from pydantic import BaseModel, RootModel


class Attribute(BaseModel):
    Type: str
    Name: str
    ShortName: str
    ToolTip: str
    MinimumValue: float
    MaximumValue: float


class Attributes(RootModel):
    root: dict[str, Attribute]

    @classmethod
    def load(cls, file_path: str = None) -> "Attributes":
        if not file_path:
            file_path = "attributes.json"
        with open(file_path, "r") as f:
            data = json.load(f)
            return cls.model_validate(data)

    def dump(self, file_path: str = None) -> str:
        if not file_path:
            file_path = "attributes.json"
        with open(file_path, "w") as f:
            json.dump(self.model_dump(), f, indent=4)
        return json.dumps(self.model_dump(), indent=4)

    def add(self, key: str, attribute: Attribute):
        self.root[key] = attribute
        self.dump()

    def update(self, key: str, attribute: Attribute):
        if key in self.root:
            self.root[key] = attribute
            self.dump()
        else:
            raise KeyError(f"No attribute found with key: {key}")

    def remove(self, key: str):
        self.root.pop(key)
        self.dump()
