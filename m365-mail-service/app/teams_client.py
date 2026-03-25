"""
Microsoft Teams client voor lc-mail-service.
Haalt berichten op uit Teams channels via Microsoft Graph API.
Vereist extra permission: ChannelMessage.Read.All (delegated)
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional


def fetch_teams_messages(
    mailbox: Dict[str, Any],
    hours_back: int = 24,
    max_teams: int = 5,
    max_messages_per_channel: int = 10,
) -> List[Dict[str, Any]]:
    """
    Haal recente Teams berichten op voor de gebruiker.
    Geeft lijst van dicts met team, channel en berichten.
    """
    from .graph import get_access_token, graph_get

    access_token = get_access_token(mailbox)
    since = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    since_str = since.isoformat()

    results = []

    try:
        # Haal joined teams op
        teams_data = graph_get(access_token, "/me/joinedTeams", params={"$select": "id,displayName"})
        teams = teams_data.get("value", [])[:max_teams]
    except Exception as e:
        return [{"error": f"Teams ophalen mislukt: {str(e)}"}]

    for team in teams:
        team_id = team.get("id")
        team_name = team.get("displayName", "Onbekend team")

        try:
            # Haal channels op
            channels_data = graph_get(
                access_token,
                f"/teams/{team_id}/channels",
                params={"$select": "id,displayName"}
            )
            channels = channels_data.get("value", [])[:3]  # max 3 channels per team
        except Exception:
            continue

        for channel in channels:
            channel_id = channel.get("id")
            channel_name = channel.get("displayName", "Algemeen")

            try:
                msgs_data = graph_get(
                    access_token,
                    f"/teams/{team_id}/channels/{channel_id}/messages",
                    params={
                        "$top": max_messages_per_channel,
                        "$filter": f"createdDateTime ge {since_str}",
                        "$select": "id,createdDateTime,from,body,subject,importance",
                    }
                )
                messages = msgs_data.get("value", [])
            except Exception:
                continue

            if not messages:
                continue

            parsed = []
            for m in messages:
                sender = m.get("from", {})
                user = sender.get("user", {}) if sender else {}
                body = m.get("body", {})
                content = body.get("content", "") if body else ""
                # Strip HTML tags (simpel)
                import re
                content_plain = re.sub(r"<[^>]+>", "", content).strip()[:300]

                parsed.append({
                    "datum": m.get("createdDateTime", "")[:16].replace("T", " "),
                    "van": user.get("displayName", "Onbekend"),
                    "bericht": content_plain,
                    "belang": m.get("importance", "normal"),
                })

            if parsed:
                results.append({
                    "team": team_name,
                    "channel": channel_name,
                    "berichten": parsed,
                })

    return results
