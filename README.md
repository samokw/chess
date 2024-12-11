# Game Server Instructions for macOS

## Build the Project
Clone the project locally, then run the following command to build the project:
```
make
```

## Start the Server
Start the server using Python:
```
python server.py <port>
````
The server will start and listen on the network card.

## Join the Game
To join the game in the browser paste one of the following options in the browser:

- **Localhost**:
```
localhost: <port>
```

- **IP Address of the Machine Running the Server**:
```
<ip address of machine running server>:<port>
```
