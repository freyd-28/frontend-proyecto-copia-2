import os
from src import create_app

app = create_app(os.getenv("FLASK_CONFIG", "development"))


if __name__ == "__main__":
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "5001")),
        debug=app.config.get("DEBUG", True),
    )