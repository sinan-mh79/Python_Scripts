from app import app  # if you are importing app directly
from waitress import serve

if __name__ == "__main__":
    # Waitress is a production-ready server (faster than Flask built-in)
    serve(app, host="0.0.0.0", port=5000)
