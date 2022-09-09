import os

from flask import Flask, request

app = Flask(__name__)
file_name = 'workers.txt'


@app.route('/')
def get_workers():
    with open(file_name, 'r') as f:
        worker = request.args.get("worker_id")
        for line in f.readlines():
            if worker.lower() in line.lower():
                return "true"
        return "false"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
