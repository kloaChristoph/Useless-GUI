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
    conn : socket.socket
        A TCP/IPv4 connection to allow clients to connect to the server
    que : multiprocessing.Queue
        A que to receive multiple commands at once
    listeners : list[multiprocessing.Process] (default: [])
        A list of processes to receive data simultaneously

    Methods
    -------
    send(conn: socket.socket, data: bytes) -> None
        Send data to the client (first length then data)
    recv(conn: socket.socket) -> bytes
        Function to receive the exact amount of bytes
    accept_clients(amount: int = 4) -> None
        Allow 'amount' clients to connect to the Server
    send_all(command: str, **data) -> None
        Send a command to every client in self.clients
    send_to(command: str, username: str, **data) -> None
        Send data to a Client
    receive(name: str) -> str | None
        Receive data from a client
    receive_from_client(client) -> list[dict] | dict
        Listen to ONE response of a client
    allow_responses_from(*clients: str) -> None
        Start processes for every given client and listen if they are sending commands
    stop_responses() -> None
        Close all running listeners
    wait_for_response(client: str) -> None
        Wait for Responses from a client
    """
    def __init__(self, db: database.Database , host: str = "127.0.0.2", port: int = 3333):
        """
        Initialize a new NetworkServer to handle the network

        Parameters
        ----------
        db: database.Databse
            The Database in which the accounts are stored
        host : str
            The IP-Address the server will be bind to
        port : int
            The Port the server will be bind to
        """
        self.db = db
        self.clients: dict[str, ClientData] = {}
        self.ENCODING = "utf-8"
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.que: multiprocessing.Queue = multiprocessing.Queue()
        self.listeners: list[multiprocessing.Process] = []

        print(f"[{'LISTENING':<10}] Bound to the port: {host}:{port}")
        self.server_socket.bind((host, port))

#-------------------------CONNECT-------------------------#

    def accept_clients(self, amount: int = 10) -> None:
        """
        Allow 'amount' clients to connect to the Server

        Receive the name and store them as a ClientData

        Parameters
        ----------
        amount : int
            How many clients are able to connect

        Returns
        -------
        None
        """
        self.server_socket.listen()

        while len(self.clients) < amount:
            name = ""
            conn, addr = self.server_socket.accept()

            data = self.receive_from_client(conn=conn)

            if data.get("command") == "LOGIN":
                
                name = data.get("from")

                if name in self.clients:
                    #there is already a client with that name
                    self.send(conn, json.dumps({"command": "CONNECTION_REFUSED"}).encode(self.ENCODING))
                    conn.close()
                
                #checking if the user exists and if the password is correct
                #TODO:
                elif self.db.verify_user(name, data.get("password")):
                    self.clients[name] = ClientData.new_conn(name, conn, addr)
                    print(f"[{'CONNECTION':<10}] {name} connected to the Game {len(self.clients)}/{amount} ({addr[0]}:{addr[1]})")
                    self.send_to("CONNECTED", name)
                else:
                    self.send(conn, json.dumps({"command": "CONNECTION_REFUSED"}).encode(self.ENCODING))
                    conn.close()


            elif data.get("command") == "REGISTER":
                pass

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

    def send_to(self, command: str, username: str, **data: Any) -> None:
        """
        Send data to a Client

        Parameters
        ----------
        command : str
            The command the Client should receive
        username : str
            The username the command should be sent to
        data : any
            Additional data the client needs
        Returns
        -------
        None
        """
        if username not in self.clients:
            return None
        
        to_send = {"command": command,
                   "to": username}

        if data:
            for key, value in data.items():
                to_send[key] = value

        string_data = json.dumps(to_send)
        print(f"[{'SENDING':<10}] {string_data}")

        self.send(self.clients[username].conn, string_data.encode(self.ENCODING))

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
        bytes : The data received
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
            None if the name of the client is not given in self.clients
        """
        
        received = self.recv(conn).decode(self.ENCODING)
        return received


    def receive_from_client(self, conn: socket.socket) -> list[dict] | dict:
        """
        Listen to ONE response of a client
        (sometimes can be more commands than one)

        Parameters
        ----------
        client: socket.socket
            The client to receive the command(s) from

        Returns
        -------
        dict : One Command
        list[dict] : Multiple Commands
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
    
    def __eq__(self, other: object) -> bool:
        """
        Checks if a socket is the same as the socket of the Client

        Parameters
        ----------
        other : CardBase | int
            The other socket you want to compare with the stored socket

        Returns
        -------
        bool : If it's te same socket
        """

        if isinstance(other, socket.socket):
            if self.conn == other:
                return True
            else:
                return False
    
