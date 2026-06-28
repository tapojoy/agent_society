import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "gateway.log"

# logging.basicConfig(
#     level=logging.INFO,
#     format=(
#         "%(asctime)s | "
#         "%(levelname)s | "
#         "%(message)s"
#     ),
#     handlers=[
#         logging.FileHandler(LOG_FILE),
#         logging.StreamHandler()
#     ]
# )

logger = logging.getLogger("ollama_gateway")

logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    # "%(asctime)s | %(levelname)s | %(message)s"
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)


file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,
    backupCount=5
)

file_handler.setFormatter(formatter)


console_handler = logging.StreamHandler()

console_handler.setFormatter(formatter)


logger.handlers.clear()

logger.addHandler(file_handler)

logger.addHandler(console_handler)

logger.propagate = False

