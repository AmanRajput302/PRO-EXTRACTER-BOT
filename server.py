from flask import Flask
import multiprocessing
import os
import subprocess

app = Flask(__name__)
bot_process = None

def run_bot():
    # Bot ko waise hi run kar jaise normally "python -m Extractor" chalate ho
    subprocess.call(["python", "-m", "Extractor"])

@app.route("/")
def home():
    global bot_process
    if bot_process is not None and bot_process.is_alive():
        return "✅ Bot running"
    else:
        return "❌ Bot stopped"

if __name__ == "__main__":
    # Start bot process
    bot_process = multiprocessing.Process(target=run_bot)
    bot_process.start()

    # Start flask server
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
