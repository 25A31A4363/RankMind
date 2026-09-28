import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)

APP_NAME = "RankMind SEO & Search Intelligence Agent"
API_V1_PREFIX = "/api/v1"
DEFAULT_FLAGSHIP_QUERY = "best python courses for beginners"
DEFAULT_TARGET_DOMAIN = "learnpythonhub.io"
