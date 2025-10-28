from app import create_app
import os

app = create_app()  # ✅ Create the app using the factory function

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # For Render or local
    app.run(host="0.0.0.0", port=port, debug=True)
