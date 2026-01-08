import getpass

from core.client import Client
from core.config import Config
from core.utils import get_app_version

def main():
    config: Config = Config()
    client: Client = Client(config)
    
    print(f"Juicebox {get_app_version()}")

    running: bool = True

    while running:
        command: str = input("> ")

        match command.split(" ")[0]:
            case "/find":
                parts: list[str] = command.split(" ")
                target: str = "" if len(parts) == 1 else parts[1]
                
                candidates: list[tuple] = client.find(target)

                if not candidates:
                    print("No available servers")
                else:
                    for (address, port) in candidates:
                        print(f"- {address} : {port}")
            case "/connect":
                parts: list[str] = command.split(" ")

                if len(parts) != 3:
                    print("Please pass the address and port of the server")
                else:
                    name: str = get_input("Username: ")
                    password: str = get_input("Password (Leave empty for no password): ", hidden=True, optional=True)

                    print(client.connect(name=name, password=password, address=(parts[1], int(parts[2]))))
            case "/disconnect":
                success: bool = client.disconnect()
                print("Disconnected from Juicebox server." if success else "Failed to disconnect from Juicebox server.")
            case "/queue":
                parts: list[str] = command.split(" ")

                if len(parts) != 2:
                    print("Please pass the Youtube song or playlist url")
                else:
                    print(client.queue(parts[1]))
            case "/skip":
                print(client.skip())
            case "/list":
                playlist: list[dict] = client.get_playlist()

                if playlist:
                    print("Nothing in queue")
                else:
                    for song in playlist:
                        print(f"- {song["duration"]} : {song["title"]} | Requested by {song["requestor"]}")
            case "/exit":
                running = False
            case _:
                print("Commands:")
                print("- /find <server-name (optional)> : Find available Juicebox server")
                print("- /connect <address> <port> : Connect to a Juicebox server")
                print("- /disconnect : Disconnect from Juicebox server")
                print("- /queue <url> : Queue a song/playlist from Youtube")
                print("- /skip : Skip current song")
                print("- /list : List songs in queue")
                print("- /exit : Exit the client")

def get_input(prompt: str, hidden: bool = False, optional: bool = False) -> str:
    while True:
        value: str = ""

        if hidden:
            value = getpass.getpass(prompt=prompt)
        else:
            value = input(prompt)

        if value or optional:
            return value


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass