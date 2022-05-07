import tkinter as tk
import socket
from threading import Thread, Event
from select import select
from warnings import warn


# server address
HOST = '127.0.0.1'
PORT = 28344


def disable(elem):
    elem.config(state=tk.DISABLED)


def enable(elem):
    elem.config(state=tk.NORMAL)


class Chat_window:
    def __handle_readable(self):
        if self.com_con in self.readable:
            self.server.send(self.com_con.recv(4096))
        if self.server in self.readable:
            data = self.server.recv(4096)
            if data:
                self.add_message(data.decode('utf-8'))
            else:
                self.server.close()
                self.inputs.remove(self.server)
                self.exit_event.set()
                self.com_sender.send(b'q')

    def __handle_writable(self):
        warn('реализуй')

    def __handle_exceptional(self):
        warn('реализуй')

    def __create_com_listener(self):
        com_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        com_listener.bind((COM_LISTENER_HOST, COM_LISTENER_PORT))
        com_listener.setblocking(False)
        com_listener.listen()
        return com_listener

    def __create_com_sender(self):
        com_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        com_sender.connect((COM_LISTENER_HOST, COM_LISTENER_PORT))
        com_sender.setblocking(False)
        return com_sender

    def __tarfun(self):
        self.com_listener = self.__create_com_listener()
        self.com_sender = self.__create_com_sender()
        self.com_con, _ = self.com_listener.accept()
        self.com_con.setblocking(False)

        self.inputs = [self.server, self.com_con]
        self.outputs = []

        self.exit_event = Event()

        while True:
            (self.readable,
             self.writable,
             self.exceptional) = select(self.inputs,
                                        self.outputs,
                                        self.inputs)
            if self.exit_event.is_set():
                break
            self.__handle_readable()
            self.__handle_writable()
            self.__handle_exceptional()

        for elem in [self.server, self.com_listener,
                     self.com_sender, self.com_con]:
            elem.close()

    def __init__(self, username):
        self.username = username

        self.window = tk.Tk()

        self.f_top = tk.Frame(self.window)
        self.f_bot = tk.Frame(self.window)
        self.f_top.pack()
        self.f_bot.pack()

        # Text
        self.txtbox = tk.Text(self.f_top, width=50, height=10)
        self.txtbox.pack(side=tk.LEFT)
        disable(self.txtbox)

        # scroll
        self.scroll = tk.Scrollbar(self.f_top, command=self.txtbox.yview)
        self.scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.txtbox.config(yscrollcommand=self.scroll.set)

        # Entry
        self.entry = tk.Entry(self.f_bot, width=50)
        self.entry.pack(side=tk.LEFT)

        # send Button
        self.send_btn = tk.Button(self.f_bot, text='Send', width=10,
                                  height=1, command=self.__send_btn_click)
        self.send_btn.pack(side=tk.LEFT)

        # connect to server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((HOST, PORT))
        self.server.setblocking(False)

        # start connection thread
        con_thread = Thread(target=self.__tarfun)
        con_thread.start()

        self.window.mainloop()

    def __send_btn_click(self):
        message = self.entry.get()
        self.server.send((self.username + ' : ' + message).encode('utf-8'))
        self.add_message(self.username + ' : ' + message)

    def add_message(self, message):
        enable(self.txtbox)
        self.txtbox.insert(1.0, message + '\n')
        disable(self.txtbox)


class Name_window:
    def __init__(self):
        self.window = tk.Tk()

        self.label = tk.Label(self.window, text='Your name:')
        self.label.pack()

        self.txtbox = tk.Entry(self.window)
        self.txtbox.pack()

        def go_button_click():
            self.username = self.txtbox.get()
            self.window.destroy()

        self.button = tk.Button(self.window, text='GO',
                                command=go_button_click)
        self.button.pack()

        self.username = None
        self.window.mainloop()


def choose_port():
    with open('port.txt', 'r') as f:
        s = f.readline()
        if s == '0':
            flag = 1
            port = 17451
        else:
            flag = 0
            port = 17452

    with open('port.txt', 'w') as f:
        f.write(str(flag))

    return port


if __name__ == '__main__':
    COM_LISTENER_PORT = choose_port()
    COM_LISTENER_HOST = '127.0.0.1'
    nwin = Name_window()
    username = nwin.username
    if username is None:
        quit()
    chwin = Chat_window(username)
