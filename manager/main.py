import argparse
import os
import socket
import time
import uuid
from multiprocessing import Queue, Process, Event
from threading import Thread, Semaphore

import torchvision.transforms as transforms
from PIL import Image
from base58 import b58encode
from flask import Flask, request, abort, send_file
from flask_socketio import SocketIO

from errors import ApiTaskFailNoFileField, ApiTaskFailFileIsEmpty
from util import fail_result, success_result, ensure_path

FLICKR_ALPHABET = b'123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'

# parse command line options before launching.
parser = argparse.ArgumentParser(description='CS655 Image Recognition Daemon')
parser.add_argument("total_img_num", type=int, help="Specify image numbers in total")
parser.add_argument("required_workers_num", type=int, help="The number of workers")
parser.add_argument("--hostname", "-i", type=str, default="0.0.0.0",
                    help="Setting the hostname running the server")
parser.add_argument("--port", "-p", type=int, default=80, help="Setting the server port")
parser.add_argument("--debug", "-g", action="store_true", default=False,
                    help="Whether to use debug mode.")
parser.add_argument("--dir-temp", dest="temp", type=str, default="temp", help="Store temporary files in a directory")

command_line_args = parser.parse_args()
# 运行后端服务器所需的变量
backend_server_hostname = command_line_args.hostname
backend_server_port = command_line_args.port
backend_server_use_debug = command_line_args.debug
temp_image_dir = command_line_args.temp

app = Flask(__name__)
# random choose a system generated number as secret key.
app.secret_key = os.urandom(16)
# update HTTP server to WebSocket server.
socketio = SocketIO(app, cors_allowed_origins='*')

total_img_num = command_line_args.total_img_num
required_workers_num = command_line_args.required_workers_num  # set 1-5
semaphore = Semaphore(required_workers_num)
workers_limit = required_workers_num + 1
conn_pool = []
images = Queue(maxsize=20)
idle_workers = Queue(maxsize=5)
buffer_size = 1024
img_num_count = 0
total_img_size = 0  # bit
start_time = 0.0
total_time = 0.0  # second
last_img_id = {
    0: "",
    1: "",
    2: ""
}
results = {"": ""}


def check_if_work():
    global images, idle_workers
    if (not images.empty()) and (not idle_workers.empty()):
        return True
    else:
        return False


def get_image(image_id):
    img = Image.open(os.path.join(temp_image_dir, image_id)).convert('RGB')
    img = transforms.ToTensor()(img)
    row = img.shape[1]
    column = img.shape[2]
    ss = image_id + " " + str(row) + " " + str(column) + " "
    img_numpy = img.numpy().flatten()
    for num in img_numpy:
        ss += str(num) + ' '
    return ss


def collect_image_result(msg):
    decoded_result = msg.split(" ", 1)
    msg_id = decoded_result[0]
    result = decoded_result[1].split("\n")[0]
    return msg_id, result


def output_statistics():
    global total_img_size, total_time
    print("---------------- statistics -------------------")
    print(results)
    print("Total Image Size: " + str(total_img_size) + "bits")
    print("Total Time: " + str(total_time) + "seconds")
    throughput = total_img_size / total_time
    print("Throughput: " + str(throughput) + "bps")


def snd_rcv_img(img_id):
    global start_time, img_num_count, images, conn_pool, \
        workers_limit, idle_workers, last_img_id, results, \
        total_img_size, total_img_num, total_time

    semaphore.acquire()
    _id = idle_workers.get()
    worker = conn_pool[_id]
    img_msg = get_image(img_id) + "\n"

    try:

        while True:
            worker.send(img_msg.encode("utf-8"))
            print(">>> Send one image to worker" + str(_id + 1))
            print(time.time())
            timer = Timer(20, worker, _id, img_msg)
            timer.start()
            msg = ""

            while True:
                feedback = worker.recv(buffer_size)
                msg += feedback.decode("utf-8")
                if msg[-1] == '\n':
                    timer.cancel()
                    break

            if msg == "404\n":
                print(">>> Detected disconnection with Worker" + str(_id + 1))
                timer.cancel()
                images.put(img_id)
                raise Exception
            print(">>> Receive from the server: " + msg)
            print(time.time())
            this_img_id, this_result = collect_image_result(msg)

            if this_img_id == last_img_id[_id]:
                continue
            else:
                last_img_id[_id] = this_img_id
                results[this_img_id] = this_result
                socketio.emit("result", {
                    "task_id": this_img_id,
                    "result": this_result,
                })
                total_img_size += len(img_msg.encode("utf-8")) * 8
                img_num_count += 1

                if img_num_count == total_img_num:
                    total_time = time.time() - start_time
                    output_statistics()
                    img_num_count = 0
                break

        idle_workers.put(_id)
        semaphore.release()

    except Exception as e:
        print(e)
        # Handle if one worker failed
        conn_pool[_id].close()
        if workers_limit < 4:  # set 5
            idle_workers.put(workers_limit - 1)
            print(">>> Start assigning works to Worker" + str(workers_limit))
            workers_limit += 1
            semaphore.release()
        else:
            print(">>> There is no available worker anymore.")


# Timer Class
class Timer(Process):
    def __init__(self, interval, worker, _id, img_msg):
        super(Timer, self).__init__()
        self.interval = interval
        self.worker = worker
        self.id = _id
        self.img_msg = img_msg
        self.finished = Event()

    def cancel(self):
        self.finished.set()

    def run(self) -> None:
        while not self.finished.wait(self.interval):
            self.worker.send(self.img_msg.encode("utf-8"))
            print(">>> Timeout! Send the image again to worker" + str(self.id + 1))


def main():
    global conn_pool, idle_workers, required_workers_num, images, start_time, img_num_count

    # Build connection with workers
    manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    manager_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    manager_socket3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    manager_socket.bind(("10.10.1.1", 2888))
    manager_socket2.bind(("10.10.2.1", 2889))
    manager_socket3.bind(("10.10.3.1", 2890))

    manager_socket.listen(5)
    manager_socket2.listen(5)
    manager_socket3.listen(5)
    print(">>> Manager starts. Connecting to workers...")

    i = 0
    worker, addr = manager_socket.accept()
    conn_pool.append(worker)
    if i < required_workers_num:
        idle_workers.put(i)
    i += 1
    print(">>> Connected to worker1")

    worker2, addr2 = manager_socket2.accept()
    conn_pool.append(worker2)
    if i < required_workers_num:
        idle_workers.put(i)
    i += 1
    print(">>> Connected to worker2")

    worker3, addr3 = manager_socket3.accept()
    conn_pool.append(worker3)
    if i < required_workers_num:
        idle_workers.put(i)
    i += 1
    print(">>> Connected to worker3")

    print(">>> Connected with all 3 nodes")


@app.route('/api/task', methods=["POST", "OPTIONS"])
def handle_picture():
    global start_time

    if request.method == 'POST':
        # 读取 forms 中的 file 数据，并进行存储
        if 'file' not in request.files:
            return fail_result(ApiTaskFailNoFileField)

        file = request.files['file']
        # 如果用户没有选择文件，浏览器将提交一个没有文件名的空 file。
        if file.filename == "":
            return fail_result(ApiTaskFailFileIsEmpty)

        # 生成一个任务 id，供前端使用
        uuid_byte = uuid.uuid4().bytes
        short_uuid = b58encode(uuid_byte, FLICKR_ALPHABET)
        str_uuid = short_uuid.decode()

        # 这一步要保存文件
        file.save(get_temp_name(str_uuid))

        # create new thread for the image
        print(">>> Get one image: " + str_uuid)
        if img_num_count == 0:
            start_time = time.time()
        worker_thread = Thread(target=snd_rcv_img, args=(str_uuid,))
        worker_thread.setDaemon(True)
        worker_thread.start()

        # 最后，返回任务 id 给前端
        return success_result(task_id=str_uuid)

    elif request.method == 'OPTIONS':
        return """Usage:
  Upload a new picture (to submit an image recognition task). Manager will return a task id from the front end.
- METHOD: POST
- Parameter Format: Form data/FILE
- Return Format: JSON
- Return Data: { "task_id": <task_id, type: string, format: base58 of an random generated uuid> }
"""


def get_temp_name(filename: str):
    ok_temp_dir = ensure_path(temp_image_dir)
    return os.path.join(ok_temp_dir, filename)


@app.route('/upload/<task_id>', methods=["GET"])
def access_temp_img(task_id: str):
    file_path = get_temp_name(task_id)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_file(file_path, task_id)
    else:
        abort(404)


@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path:path>', methods=["GET"])
def frontend(path: str):
    return app.send_static_file(path)


@socketio.on('connect')
def on_ws_connection():
    print("A client connected to ws.")


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


def run_backend_server():
    main()

    print(f"""Manager details:
total_img_num: {total_img_num}
required_workers_num: {required_workers_num}
workers_limit: {workers_limit}
""")
    print(f"""Server run on {backend_server_hostname}:{
    backend_server_port}{', as debug mode' if backend_server_use_debug else ''}""")
    print(f"Directory used to store files is '{temp_image_dir}'")

    socketio.run(app, host=backend_server_hostname,
                 port=backend_server_port,
                 debug=backend_server_use_debug, use_reloader=False)


if __name__ == '__main__':
    run_backend_server()
