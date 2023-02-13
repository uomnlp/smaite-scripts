import json
import os

from flask import Flask, request
from flask_cors import CORS
from gevent.pywsgi import WSGIServer

app = Flask(__name__)
CORS(app)

file_name = 'workers.txt'
auth_key = 'Asdf1234'



if __name__ == '__main__':
    with open(file_name, 'r') as f:
        workers = set(l for l in f.read().splitlines() if l)
    
    @app.route('/save', methods=['POST'])
    def save_workers():
        worker = request.args.get("worker_id", None)
        key = request.args.get("key", None)
        if worker and key:
            if key != auth_key:
                print("Wrong auth key")
                return "false"
            else:
                print(f"Adding {worker}!")
                workers.add(worker)
                return "true"
        return "false"

    @app.route('/', methods=['GET'])
    def get_workers():
        worker = request.args.get("worker_id", None)
        if worker:
            return json.dumps(worker in workers)
        else:
            return json.dumps(False)

    


    port = int(os.environ.get('PORT', 5000))
#    app.run(host='0.0.0.0', port=port)
    server = WSGIServer(('', port), app)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        server.close()
        print("Saving workers")
        with open(file_name, 'w+') as f:
            f.write('\n'.join(workers) + '\n')
