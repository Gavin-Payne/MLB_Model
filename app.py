from flask import Flask, render_template
import subprocess
from waitress import serve

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_python_program')
def run_python_program():
    result = subprocess.run(['python3', 'MLB.py'], capture_output=True, text=True)
    return result.stdout

@app.route('/history')
def history():
    return render_template('history.html')

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=8000)