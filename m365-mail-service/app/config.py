import os


class Settings:
    def __init__(self) -> None:
        self.tenant_id = os.getenv("M365_TENANT_ID", "common")
        self.client_id = os.getenv("M365_CLIENT_ID", "")
        self.client_secret = os.getenv("M365_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("M365_REDIRECT_URI", "http://192.168.30.123:8010/auth/callback")
        self.scopes = os.getenv(
            "M365_SCOPES",
            "offline_access https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/User.Read",
        ).split()
        self.database_path = os.getenv("M365_DB_PATH", "data/mailboxes.sqlite3")
        self.graph_base = os.getenv("GRAPH_BASE_URL", "https://graph.microsoft.com/v1.0")

    def ensure_oauth_ready(self) -> None:
        missing = []
        if not self.client_id:
            missing.append("M365_CLIENT_ID")
        if not self.client_secret:
            missing.append("M365_CLIENT_SECRET")
        if not self.redirect_uri:
            missing.append("M365_REDIRECT_URI")
        if missing:
            raise RuntimeError(f"Missing required env var(s): {', '.join(missing)}")


settings = None


def get_settings() -> Settings:
    global settings
    if settings is None:
        settings = Settings()
    return settings
