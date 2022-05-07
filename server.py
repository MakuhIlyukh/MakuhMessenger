'''
Сервер для чата
'''


import socket
from select import select
from queue import Queue
from queue import Empty
from threading import Thread, Event


HOST = '127.0.0.1'
PORT = 28344


def open_prepare_server_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.bind((HOST, PORT))
    sock.listen(10)
    return sock


def access_event(s):
    '''if need to access'''
    return s is sock


def close_event(data):
    '''if need to close the connection'''
    return not bool(data)


def create_new_connection():
    '''sock - main socket'''
    conn, _ = sock.accept()
    conn.setblocking(False)
    inputs.append(conn)
    client_socks.append(conn)
    message_queues[conn] = Queue()
    print('new connection was created')


def close_connection(s):
    '''s not is sock!'''
    if s in outputs:
        outputs.remove(s)
    inputs.remove(s)
    client_socks.remove(s)
    s.close()
    message_queues.pop(s, None)
    print('connection was closed')


def handle_input_message(s, data):
    '''we have input message in data, let's handle it'''
    global outputs
    for key in client_socks:
        if key is not s:
            message_queues[key].put(data)
    outputs = client_socks.copy()
    print('message was recieved')


def send_msg(s):
    '''if there is message in queue, we send it'''
    try:
        next_msg = message_queues[s].get_nowait()
    except Empty:
        outputs.remove(s)
    else:
        s.send(next_msg)
        print('message was sent')


def handle_readable():
    for s in readable:
        if access_event(s):
            create_new_connection()
        else:
            data = s.recv(4096)
            if close_event(data):
                close_connection(s)
            else:
                handle_input_message(s, data)


def handle_writable():
    for s in writable:
        send_msg(s)


def handle_exceptional():
    for s in exceptional:
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        if s is not sock:
            client_socks.remove(s)
        message_queues.pop(s, None)
        s.close()


def close_all_sockets():
    for s in client_socks:
        s.close()
    sock.close()


def start_keyboard_input_thread():
    def tarfun():
        com = ''
        while com != 'q':
            com = input()

        quit_event.set()
        # (чтобы select перестал блокировать главный цикл в main)
        quit_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        quit_sock.connect((HOST, PORT))
        quit_sock.close()

    keyboard_input_thread = Thread(target=tarfun)
    keyboard_input_thread.start()


if __name__ == '__main__':
    sock = open_prepare_server_socket()
    inputs = [sock]
    client_socks = []
    outputs = []
    message_queues = dict()
    # нужно для того, чтобы прервать select(если захотим завершить сервер)
    quit_event = Event()
    start_keyboard_input_thread()

    while True:
        print('iteration')
        readable, writable, exceptional = select(inputs, outputs, inputs)
        if quit_event.is_set():
            break
        handle_readable()
        handle_writable()
        handle_exceptional()

    close_all_sockets()
    print('all sockets were closed')
    print('end of program')
