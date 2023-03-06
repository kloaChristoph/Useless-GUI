# Commands

# Server to Client

---

### CONNECTED
    The Client is Connected Sucessfully
**Attributes:**
- to: str → Name of the Client to send the Command to
- name: str → The Name of the Client that is now connected

### CONNECTION_REFUSED
    There is already a Client connected with the given name




# Client to Server

---

### LOGIN
    The client tries to login into a account

**Attributes:**
- from: str → The Name of the Client the message comes from
- password: str → The password the user typed into to login field

### REGISTER
    The client registers a new account

**Attributes:**
- from: str → The Name of the Client the message comes from
- password: str → The password the user typed into to login field