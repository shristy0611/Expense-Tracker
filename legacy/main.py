from wsgi import app

# This file is for Gunicorn to run with main:app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
