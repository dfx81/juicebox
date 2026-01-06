import tomllib

class Config:
    def __init__(self):
        self._setup()

    def _setup(self):
        try:
            with open("config.toml", "rb") as file:
                data: dict = tomllib.load(file)

                self.motd = data["motd"]
                self.security = self._SecurityConfig(password=data["security"]["password"])
                self.server = self._ServerConfig(name=data["server"]["name"], address=data["server"]["address"], port=data["server"]["port"])
                self.storage = self._StorageConfig(downloads=data["storage"]["downloads"], database=data["storage"]["database"], archive=data["storage"]["archive"])
        except Exception:
            raise RuntimeError("Bad Configuration")

    class _SecurityConfig:
        def __init__(self, password: str = ""):
            self.password: str = password
    
    class _ServerConfig:
        def __init__(self, name: str = "Juicebox", address: str = "0.0.0.0", port: int = 8181):
            self.name: str = name
            self.address: str = address
            self.port: int = port
        
    class _StorageConfig:
        def __init__(self, downloads: str = "downloads", database: str = "data.db", archive: str = "cache.txt"):
            self.downloads: str = downloads
            self.database: str = database
            self.archive: str = archive