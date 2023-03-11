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

### UPDATE_HIGHSCORE_TABLE
    Updating the highscore table 
**Attributes:**
- to: str → Name of the Client to send the Command to
- highscores: list[list] → A list of the top 10 clients with their name and their score

### OWN_HIGHSCORE
    Sending the client his own all time highscore 
**Attributes:**
- to: str → Name of the Client to send the Command to
- rating: float → The highest rating the user reached
- score: int → The highscore of the user
- accuracy: flaot → The accuracy the user had when reaching his highscore
- time: int → The duration of the game 



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

### CLOSE_CONNECTION
    The client registers a new account

**Attributes:**
- from: str → The Name of the Client the message comes from

### NEW_HIGHSCORE
    The client reached a new highscore

**Attributes:**
- from: str → The Name of the Client the message comes from
- highscore: int → The new highscore of the user
- accuracy: float → The accuracy the user had while reaching the new highscore
- time: int → The time the user needed to reach the new highscore

### REQUEST_HIGHSCORE_TABLE
    The client requests the data for the highscore table

**Attributes:**
- from: str → The Name of the Client the message comes from

### REQUEST_OWN_HIGHSCORE
    The client requests the own all time highscore

**Attributes:**
- from: str → The Name of the Client the message comes from

