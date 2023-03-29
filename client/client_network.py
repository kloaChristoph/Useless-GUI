"""
In this file the Network part of the client is defined
~ Hartl Lorenz, Hell Andreas, Holas Christoph
"""

import json
import socket
import multiprocessing

from typing import Any


class NetworkClient:
    """
    A class to handle the network part of the client

    ...

    Constants
    ---------
    ENCODING : str -> "utf-8"
        The encoding when sending/receiving data

    Attributes
    ----------
    que : multiprocessing.Queue
        A queue to store the commands received when receiving data
    client_socket : socket.socket
        The socket to connect to the server
    listener : multiprocessing.Process
        The process to receive data from the server
    running : bool
        If the listener is running or not    
    connected : bool
        If the client is connected to the server or not

    Methods
    -------
    connect_to_server(name: str, pwd: str, register: bool = False, host: str = "127.0.0.2", port: int = 3333) -> bool | ConnectionRefusedError | None
        Connect to the server with a given name
    send(data: bytes) -> None
        Send data to the server (first length then data)
    send_to_server(command: str, username: str, **data: Any) -> None
        Send a command to the server
    recv() -> bytes
        Function to receive the exact amount of bytes
        First the length will be received than the client receives the data
    convert_received_data() -> dict | list[dict]
        Receive data from the server and convert it to a command
        (Multiple commands can be received at once)
    recv_in_process() -> None
        Function to receive data from the server and put it into the queue
    """
    
    def __init__(self):
        """
        Initialize a new NetworkClient

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.ENCODING = "utf-8"
        #A queue to store the commands received when receiving data
        self.que: multiprocessing.Queue = multiprocessing.Queue()
        #allows the communication between the client and the server
        self.client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #The process to receive data from the server
        self.listener: multiprocessing.Process = multiprocessing.Process(target=self.recv_in_process, daemon=True)
        #Indicators if listener is running and if client is connected to the server
        self.running: bool = True
        self.connected: bool = False


#-------------------------CONNECT-------------------------#

    def connect_to_server(self, name: str, pwd: str, register: bool = False, host: str = "127.0.0.2", port: int = 3333) -> bool | ConnectionRefusedError | None:
        """
        Connect to the server with a given name

        Parameters
        ----------
        name : str
            The name of the client that wants to connect to the server
        pwd : str
            The password for the login
        register : bool
            If register is True the user wants to register if not the user wants to log in into a existing account
        host : str (default: 127.0.0.2)
            The IPv4-Address of the Server to connect to
        port : int (default: 3333)
            The Port of the Server to connect to

        Returns
        -------
        self.connected: bool
            Returns if the connection was successful
        reason: str | None
            The reason why the connection was refused
        """
        try:
            self.client_socket.connect((host, port))
        except ConnectionRefusedError as error:
            return error, None
    
        if register:
            self.send_to_server(command="REGISTER", username=name, password=pwd)
        else:
            self.send_to_server(command="LOGIN", username=name, password=pwd)
        
        resp = self.convert_received_data()
        if resp.get("command") == "CONNECTED":
            if resp.get("to") == name:
                print("listener_started")
                self.listener.start()
                self.connected = True
                return self.connected, None
        elif resp.get("command") == "CONNECTION_REFUSED":
            self.client_socket.close()
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.connected = False
            return self.connected, resp.get("reason")

#-------------------------CONNECT-------------------------#



#--------------------------SEND---------------------------#

    def send(self, data: bytes) -> None:
        """
        Send data to the server (first length then data)

        Parameters
        ----------
        data : bytes
            The data to send to the server

        Returns
        -------
        None
        """
        length = len(data)
        try:
            byte_length = length.to_bytes(16, "big")
            self.client_socket.send(byte_length)
            self.client_socket.send(data)
        except OSError:
            pass


    def send_to_server(self, command: str, username: str, **data: Any) -> None:
        """
        Send a command to the server

        Parameters
        ----------
        command : str
            The command name the server should receive
        username : str
            The name of the client that sends the command
        data : dict
            Additional data the server needs to process the command

        Returns
        -------
        None
        """
        to_send = {"command": command,
                   "from": username}

        if data:
            for key, value in data.items():
                to_send[key] = value

        string_data = json.dumps(to_send)
        print(f"[{'SENDING':<10}] {string_data}")

        self.send(string_data.encode(self.ENCODING))

#--------------------------SEND---------------------------#



#-------------------------RECEIVE-------------------------#

    def recv(self) -> bytes:
        """
        Function to receive the exact amount of bytes
        First the length will be received than the client receives the data
        
        Parameters
        ----------
        None
        
        Returns
        -------
        data : bytes
            The data received
        """
        try:
            length = int.from_bytes(self.client_socket.recv(16), "big")
            data = self.client_socket.recv(length)
            return data
        except ConnectionResetError:
            return b'{"command": "CONNECTION_LOST"}'


    def convert_received_data(self) -> dict | None:
        """
        Receive data from the server and convert it to a command
        (Multiple commands can be received at once)

        Parameters
        ----------
        None

        Returns
        -------
        : dict 
            A command received from the server
        : None
            If the received data is not a valid json
        """
        data = self.recv().decode()
        print(f"[{'RECEIVED':<10}] {data}")
        try:
            return json.loads(data)
        except json.decoder.JSONDecodeError:
            return None

    def recv_in_process(self) -> None:
        """
        The method the listener will call to receive data from the server
        When a command is received it will be added to the queue

        Parameters
        ----------
        None
        
        Returns
        -------
        None
        """
        while self.running:
            recv = self.convert_received_data()
            if recv:
                if isinstance(recv, list):
                    for com in recv:
                        self.que.put(com)
                    return
                self.que.put(recv)

#-------------------------RECEIVE-------------------------#