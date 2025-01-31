import json
import time
import hashlib
import karrio.lib as lib
import karrio.core as core


class Settings(core.Settings):
    """GEODIS connection settings."""

    api_key: str
    identifier: str
    language: str = "fr"

    @property
    def carrier_name(self):
        return "geodis"

    @property
    def server_url(self):
        return (
            "https://espace-client.geodis.com/services/services-mock"
            if self.test_mode
            else "https://espace-client.geodis.com/services"
        )

    def get_token(self, service: str, data: dict) -> str:
        timestamp = "%d" % (time.time() * 1000)
        hash = hashlib.sha256(
            ";".join(
                [
                    self.api_key,
                    self.identifier,
                    timestamp,
                    self.language,
                    service,
                    json.dumps(data, separators=(",", ":")),
                ]
            ).encode("utf-8")
        ).hexdigest()

        return ";".join([self.identifier, timestamp, self.language, hash])
