import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Allow overriding port via PORT env; default to 5001.
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, port=port)
