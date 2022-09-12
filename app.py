import os

from flask import Flask, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
CORS(app)

file_name = 'workers.txt'


@app.route('/')
def get_workers():
    try:
     with open(file_name, 'r') as f:
        worker = request.args.get("worker_id")
        for line in f.readlines():
            if worker.lower() in line.lower():
                return "true"
        return "false"
    except:
        return "false"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
#    app.run(host='0.0.0.0', port=port)
    server = WSGIServer(('', port), app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        server.close()
