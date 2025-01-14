import jstruct
import karrio.lib as lib
import karrio.core as core


class Settings(core.Settings):
    """BoxKnight connection settings."""

    username: str
    password: str
    cache: lib.Cache = jstruct.JStruct[lib.Cache]

    @property
    def carrier_name(self):
        return "boxknight"

    @property
    def server_url(self):
        return "https://api.boxknight.com/v1"

    @property
    def tracking_url(self):
        return "https://www.tracking.boxknight.com/tracking?trackingNo={}"

    @property
    def auth_token(self):
        """Retrieve the auth token using the username|passwword pair
        or collect it from the cache if an unexpired token exist.
        """
        cache_key = f"{self.carrier_name}|{self.username}|{self.password}"
        auth = self.cache.get(cache_key) or {}
        token = auth.get("token")

        if token is not None:
            return token

        self.cache.set(cache_key, lambda: authenticate(self))
        new_auth = self.cache.get(cache_key)

        if any(self.depot or "") is False:
            self.depot = new_auth["depot"]

        return new_auth["token"]


def authenticate(settings: Settings):
    import karrio.providers.boxknight.error as error

    result = lib.request(
        url=f"{settings.server_url}/soap/services/LoginService/V2_1",
        data=dict(username=settings.username, password=settings.password),
        method="POST",
    )
    response = lib.to_dict(result)
    errors = error.parse_error_response(response, settings)

    if any(errors):
        raise Exception(errors)

    return dict(token=response["token"])
