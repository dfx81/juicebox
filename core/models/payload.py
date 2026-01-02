from core.models.request_type import RequestType

class Payload:
    def __init__(self, packet: str):
        self._parse(packet)

    def _parse(self, packet: str):
        data: list[str] = packet.split("\n")
        components: list[str] = data[0].split("|")

        if (len(components) == 2):
            self.arguments: str = components[1].strip()
        else:
            self.arguments: str = ""

        match components[0].strip():
            case "DISCOVERY":
                self.request: RequestType = RequestType.DISCOVER
            case _:
                self.request: RequestType = RequestType.UNKNOWN