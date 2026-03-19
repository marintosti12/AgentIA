from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    stockfish_path: str = "/usr/games/stockfish"
    stockfish_depth: int = 20
    lichess_explorer_base_url: str = "https://explorer.lichess.ovh"
    lichess_timeout: float = 10.0
    lichess_token: str = ""

    milvus_host: str = "milvus-standalone"
    milvus_port: int = 19530
    milvus_collection: str = "chess_openings"
    embedding_model: str = "all-MiniLM-L6-v2"

    youtube_api_key: str = ""
    youtube_max_results: int = 5

    mongodb_host: str = "chess-agent-mongodb"
    mongodb_port: int = 27017
    mongodb_database: str = "chess_agent"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
