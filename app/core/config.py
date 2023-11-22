from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "dev"
    LOG_LEVEL: str = "INFO"

    CHAT_USERNAME: str = "You"
    CHAT_BOTNAME: str = "Illiana"
    CHAT_TEXT_ANIMATION_SPEED: float = 0.008

    OPENAI_API_KEY: str = "OPEN_AI_API_KEY"

    LLMS: dict[str, dict[str, str | int]] = {
        "gpt-4-1106-preview": {
            "title": "GPT-4 Turbo",
            "description": """The latest GPT-4 model with improved instruction following, JSON mode, reproducible outputs, parallel function calling, and more. Returns a maximum of 4,096 output tokens. This preview model is not yet suited for production traffic.
                    """,
            "content_window": 128000,
            "training_data": "Training Data: Up to Apr 2023",
        },
        "gpt-4-vision-preview": {
            "title": "GPT-4 Turbo with vision",
            "description": """Ability to understand images, in addition to all other GPT-4 Turbo capabilties. Returns a maximum of 4,096 output tokens. This is a preview model version and not suited yet for production traffic.
                    """,
            "content_window": 128000,
            "training_data": "Training Data: Up to Apr 2023",
        },
        "gpt-4": {
            "title": "GPT-4",
            "description": "Currently points to gpt-4-0613.",
            "content_window": 8192,
            "training_data": "Training Data: Up to Sep 2021",
        },
        "gpt-4-32k": {
            "title": "GPT-4",
            "description": "Currently points to gpt-4-32k-0613.",
            "content_window": 32768,
            "training_data": "Training Data: Up to Sep 2021",
        },
        "gpt-3.5-turbo-1106": {
            "title": "Updated GPT 3.5 Turbo",
            "description": """The latest GPT-3.5 Turbo model with improved instruction following, JSON mode, reproducible outputs, parallel function calling, and more. Returns a maximum of 4,096 output tokens.
                    """,
            "content_window": 16385,
            "training_data": "Training Data: Up to Sep 2021",
        },
        "gpt-3.5-turbo-16k": {
            "title": "GPT 3.5 Turbo",
            "description": """Currently points to gpt-3.5-turbo-0613. Will point to gpt-3.5-turbo-1106 starting Dec 11, 2023.
                    """,
            "content_window": 16385,
            "training_data": "Training Data: Up to Sep 2021",
        },
    }

    VECTORSTORE_CHROMADB_DIR: str = "data/vectorstore/chromadb"

    class Config:
        env_file = ".env"


settings = Settings()
