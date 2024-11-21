from . import app

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=3000, use_reloader=True)
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt")
        exit(0)