from __future__ import annotations

import uvicorn

from proofrag.config import get_settings


def run() -> None:
    settings = get_settings()
    uvicorn.run(
        "proofrag.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
    )


if __name__ == "__main__":
    run()

