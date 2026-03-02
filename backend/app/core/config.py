from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    stockfish_path: str = "/usr/games/stockfish"
    stockfish_depth: int = 20
    lichess_explorer_base_url: str = "https://explorer.lichess.ovh"
    lichess_timeout: float = 10.0

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
