import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # PythonAnywhere uses port 5000 internally
    app.run(host="0.0.0.0", port=port)
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # PythonAnywhere uses port 5000 internally
    app.run(host="0.0.0.0", port=port)
w<<<<<<< Updated upstream
import os
from app import create_app
=======
>>>>>>> Stashed changes

# A very simple Flask Hello World app for you to get started with...

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

<<<<<<< Updated upstream
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT automatically
    app.run(host="0.0.0.0", port=port)
=======
>>>>>>> Stashed changes
