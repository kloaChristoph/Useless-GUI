"""
In this file the Network part of the server is defined
~ Hartl Lorenz, Hell Andreas, Holas Christoph
"""

import json
import socket
import database
import multiprocessing

from typing import Any

class NetworkServer:
    """
    A class to handle the network part of the server

    ...

    Constants
    ---------
    ENCODING : str -> "utf-8"
        The encoding when sending/receiving data

    Attributes
    ----------
    clients : dict[str, ClientData] (default: {})
        A dictionary of every Client
    server_socket : socket.socket
        A TCP/IPv4 connection to allow clients to connect to the server
    remove_client_queue : multiprocessing.Queue
        A que to remove clients from the clients dictionary

    Methods
    -------
    accept_clients(db: database.Database) -> None
        Allow clients to connect to the Server
    send(conn: socket.socket, data: bytes) -> None
        Send data to the client (first length then data)
    send_to(command: str, username: str, conn: socket.socket=None, **data: Any) -> None
        Send a command to a client
    recv(conn: socket.socket) -> bytes
        Function to receive the exact amount of bytes
        First the length will be received than the data
    receive(conn: socket.socket) -> str | None
        Receive data from the client
    receive_from_client(conn: socket.socket) -> list[dict] | dict
        Convert the received data to a command or list of commands
    recv_in_process(conn: socket.socket, running: bool) -> None
        Receive data from a client in a process
    process_commands(to_process: list) -> None
        Process the commands 
    send_to_all(command: str, **data: Any) -> None
        Send a command to all clients
    """

    def __init__(self, host: str = "127.0.0.2", port: int = 3333) -> None:
        """
        Initialize a new NetworkServer to handle the network

        Parameters
        ----------
        host : str
            The IP-Address the server will be bind to
        port : int
            The Port the server will be bind to
        
        Returns
        -------
        None
        """
        self.clients: dict[str, ClientData] = {}
        self.ENCODING = "utf-8"
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.remove_client_queue: multiprocessing.Queue = multiprocessing.Queue()

        print(f"[{'LISTENING':<10}] Bound to the port: {host}:{port}")
        self.server_socket.bind((host, port))


#-------------------------CONNECT-------------------------#

    def accept_clients(self, db: database.Database) -> None:
        """
        Allow clients to connect to the Server

        Parameters
        ----------
        db: database.Databse
            The Database in which the accounts are stored

        Returns
        -------
        None
        """
        self.server_socket.listen()

        while True:
            name = ""
            conn, addr = self.server_socket.accept()

            data = self.receive_from_client(conn=conn)

            name = data.get("from")

            while not self.remove_client_queue.empty():
                name: str = self.remove_client_queue.get()
                self.clients.pop(name)

            if name in self.clients:
                #there is already a client with that name
                self.send_to("CONNECTION_REFUSED", name, conn, reason="Already loged in!")
                conn.close()
                continue

            if data.get("command") == "LOGIN":
                #checking if the user exists and if the password is correct
                if db.verify_user(name, data.get("password")):
                    self.clients[name] = ClientData.new_conn(name, conn, addr)

                    print(f"[{'CONNECTION':<10}] {name} connected to the server ({addr[0]}:{addr[1]})")
                    self.send_to("CONNECTED", name)

                    listener = multiprocessing.Process(target=self.recv_in_process, args=(conn, True))
                    listener.start()

                else:
                    self.send_to("CONNECTION_REFUSED", name, conn, reason="Wrong username or password!")
                    conn.close()

            elif data.get("command") == "REGISTER":
                if db.register_user(name, data.get("password")):
                    self.clients[name] = ClientData.new_conn(name, conn, addr)

                    print(f"[{'CONNECTION':<10}] {name} connected to the server ({addr[0]}:{addr[1]})")
                    self.send_to("CONNECTED", name)

                    listener = multiprocessing.Process(target=self.recv_in_process, args=(conn, True))
                    listener.start()
                else:
                    self.send_to("CONNECTION_REFUSED", name, reason="Username not available!")

            else:
                continue

#-------------------------CONNECT-------------------------#



#--------------------------SEND---------------------------#

    def send(self, conn: socket.socket, data: bytes) -> None:
        """
        Send data to the client (first length then data)

        Parameters
        ----------
        conn : socket.socket
            The connection to the client
        data : bytes
            The data to send to the client

        Returns
        -------
        None
        """
        length = len(data)
        conn.send(length.to_bytes(16, "big"))
        conn.send(data)


    def send_to(self, command: str, username: str, conn: socket.socket=None, **data: Any) -> None:
        """
        Send a command to a client

        Parameters
        ----------
        command : str
            The command the Client should receive
        username : str
            The username the command should be sent to
        conn : socket.socket
            Uses this connection to send data if given
        data : any
            Additional data the client needs
        
        Returns
        -------
        None
        """
        
        to_send = {"command": command,
                   "to": username}

        if data:
            for key, value in data.items():
                to_send[key] = value

        string_data = json.dumps(to_send)
        print(f"[{'SENDING':<10}] {string_data}")

        if conn:
            self.send(conn, string_data.encode(self.ENCODING))
        else:
            self.send(self.clients[username].conn, string_data.encode(self.ENCODING))


    def send_to_all(self, command: str, **data: Any) -> None:
        """
        Send a command to all clients

        Parameters
        ----------
        command : str
            The command the Client should receive
        data : any
            Additional data the client needs
        
        Returns
        -------
        None
        """
        for client in self.clients.values():
            self.send_to(command, client.name, **data)

#--------------------------SEND---------------------------#



#-------------------------RECEIVE-------------------------#

    def recv(self, conn: socket.socket) -> bytes:
        """
        Function to receive the exact amount of bytes
        First the length will be received than the data

        Parameters
        ----------
        conn : socket.socket
            The connection to the client

        Returns
        -------
        data : bytes
            The data received
        """
        byte_length = conn.recv(16)
        length = int.from_bytes(byte_length, "big")
        data = conn.recv(length)
        return data


    def receive(self, conn: socket.socket) -> str | None:
        """
        Receive data from a client

        Parameters
        ----------
        conn : socket.socket
            The connection to the client
        
        Returns
        -------
        received : str | None
            The data received
            None if couldnt receive data
        """
        
        received = self.recv(conn).decode(self.ENCODING)
        return received


    def receive_from_client(self, conn: socket.socket) -> list[dict] | dict:
        """
        Convert the received data to a command or list of commands

        Parameters
        ----------
        conn: socket.socket
            The client to receive the command(s) from

        Returns
        -------
        : dict
            One Command
        commands : list[dict]
            Multiple Commands
        """
        data = self.receive(conn)
        print(f"[{'RECEIVED':<10}] {data}")
        try:
            return json.loads(data)
        except json.decoder.JSONDecodeError:
            commands = []
            commands_len = data.count("command")
            # Remove first and last {,} to be sure to add the {,} afterwards in the for loop
            partial_commands = data[1:-1].split("}{")
            if len(partial_commands) == commands_len:
                for command in partial_commands:
                    # Add the {, } to the command again to make sure it is json loadable
                    commands.append(json.loads("{" + command + "}"))
            return commands
        

    def recv_in_process(self, conn: socket.socket, running: bool) -> None:
        """
        Receive data from a client in a process

        Parameters
        ----------
        conn: socket.socket
            The connection to the client
        name: str
            The name of the client
        running: bool
            Stops the process if running is False

        Returns
        -------
        None
        """
        to_process = []
        while running:
            recv = self.receive_from_client(conn)
            if recv:
                if isinstance(recv, list):
                    for com in recv:
                        to_process.append(recv)
                        
                else:
                    to_process.append(recv)
        
            to_process, running = self.process_commands(to_process)


    def process_commands(self, to_process: list) -> list | bool:
        """
        Process the commands

        Parameters
        ----------
        to_process : list
            The commands to process

        Returns
        -------
        to_process : list
            The commands that couldnt be processed or a empty list if all commands were processed
        running : bool
            Gives the process the information if it should stop
        """
        running = True

        while to_process:
            recv: dict = to_process[0]
            name = recv.get("from")

            match recv.get("command"):

                case "CLOSE_CONNECTION":
                    running = False
                    self.clients.pop(name)
                    self.remove_client_queue.put(name)
                    break
                
                case "NEW_HIGHSCORE":
                    score: int = recv.get("highscore")
                    accuracy: float = recv.get("accuracy")
                    time: int = recv.get("time")
                    process_db = database.Database()
                    process_db.updat_highscore(name, score, accuracy, time)

                    highscores = process_db.get_highscores()

                    process_db.close_conn()
                    self.send_to("UPDATE_HIGHSCORE_TABLE", name, highscores = highscores)

                case "REQUEST_HIGHSCORE_TABLE":
                    process_db = database.Database()
                    highscores = process_db.get_highscores()
                    process_db.close_conn()
                    
                    self.send_to("UPDATE_HIGHSCORE_TABLE", name, highscores = highscores)

                case "REQUEST_OWN_HIGHSCORE":
                    process_db = database.Database()
                    highscore = process_db.get_user_highscore(name)
                    process_db.close_conn()

                    self.send_to("OWN_HIGHSCORE", name, rating = highscore[0], score = highscore[1], \
                                 accuracy = highscore[2], time = highscore[3])

            to_process.pop(0)   
        return to_process, running

#-------------------------RECEIVE-------------------------#



class ClientData:
    """
    A class to represent a Client including all the needed client Data.

    ...

    Attributes
    ----------
    name : str
        The name of the Client
    conn : socket.socket (default: None)
        The connection to the Client
    addr : tuple[str, int] (default: None)
        The address the connection was established to (client side)

    ClassMethod
    -----------
    new_conn(name: str, conn: socket.socket, addr: tuple[str, int]) -> ClientData
        Create a new Data object using the given parameters
    """
    def __init__(self, name: str, conn: socket.socket = None, addr: tuple[str, int] = None) -> None:
        """
        Initialize all necessary attributes for the client object

        Parameters
        ----------
        name : str
            The name of the Client
        conn : socket.socket (default: None)
            The connection to the Client
        addr : tuple[str, int] (default: None)
            The address the connection was established to (client side)
        
        Returns
        -------
        None
        """
        self.name: str = name
        self.conn: socket.socket | None = conn
        self.addr: tuple[str, int] | None = addr

    @classmethod
    def new_conn(cls, name: str, conn: socket.socket, addr: tuple[str, int]) -> "ClientData":
        """
        A new connection was established and all the wanted data is saved in this object

        Parameters
        ----------
        name : str
            The name of the Client
        conn : socket.socket (default: None)
            The connection to the Client
        addr : tuple[str, int] (default: None)
            The address the connection was established to (client side)

        Returns
        -------
        ClientData : The new ClientData object
        """
        return cls(
            name,
            conn,
            addr
        )
    
