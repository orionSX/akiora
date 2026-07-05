import sys

if __name__ == "__main__":
    arg = sys.argv[1]
    if arg == "api":
        from granian import Granian
        from utils.settings import settings

        server = Granian(
            target="gateways.api.main:create_app",
            address=settings.core_host,
            port=settings.core_port,
            interface="asgi",
            factory=True,
        )
        server.serve()
    else:
        raise ValueError("There should be 1 arg: api")
