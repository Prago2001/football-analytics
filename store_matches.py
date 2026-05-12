from pathlib import Path
import re
from typing import Dict
import argparse
from parser.parse_events import EventsDataParser
from parser.parse_stats import StatsParser
from scraper.match_scraper import ScrapeMatchData


def _slug(value: str) -> str:
    """Simple filesystem-safe slug for folder names."""
    value = re.sub(r"[^A-Za-z0-9]+", "-", str(value).strip())
    value = value.strip("-").lower()
    return value or "unknown"


def build_match_directory(match_metadata: Dict, base_dir: str = "data/matches") -> Path:
    """Build a directory path of the form

    data/matches/<competition_HOME_TEAM_AWAY_TEAM_DATE>

    using parsed match metadata from EventsDataParser.
    """
    competition = (
        match_metadata.get("competition_code")
        or match_metadata.get("competition_name")
        or "competition"
    )
    home = match_metadata.get("home_team_name") or "home"
    away = match_metadata.get("away_team_name") or "away"

    # local_date is typically an ISO date or datetime string; only keep the date part
    date_str = match_metadata.get("local_date") or ""
    if isinstance(date_str, str) and date_str:
        date_token = date_str[:10]
    else:
        date_token = "unknown-date"

    folder = f"{_slug(competition)}_{_slug(home)}_{_slug(away)}_{_slug(date_token)}"
    match_dir = Path(base_dir) / folder
    match_dir.mkdir(parents=True, exist_ok=True)
    return match_dir


def scrape_and_store_match(
    link: str, base_dir: str = "data/matches", headless=False
) -> Path:
    """Scrape a single match and store its data in per-match parquet files.

    The directory structure is:

        data/matches/<competition_HOME_TEAM_AWAY_TEAM_DATE>/
            metadata.parquet
            events.parquet
            qualifiers.parquet
            stats.parquet

    Args:
        link: Full Opta/Opta Analyst match-centre URL.
        base_dir: Root directory under which match folders are created.
        headless: False. Opens google chrome by default

    Returns:
        Path to the directory where this match's parquet files were written.
    """
    print(f"Scraping data for URL {link}")
    match_scraper = ScrapeMatchData(headless=headless)
    events_obj, stats_obj = match_scraper.scrape(link)

    # Parse events, qualifiers and metadata
    events_parser = EventsDataParser(events_obj)
    df_events, df_qualifiers = events_parser.parse_events_and_qualifiers()
    df_metadata = events_parser.create_metadata_dataframe()

    match_dir = build_match_directory(events_parser.match_metadata, base_dir=base_dir)

    # One parquet per logical table for this match
    (match_dir / "events.parquet").parent.mkdir(parents=True, exist_ok=True)
    df_events.to_parquet(match_dir / "events.parquet", index=False)
    df_qualifiers.to_parquet(match_dir / "qualifiers.parquet", index=False)
    df_metadata.to_parquet(match_dir / "metadata.parquet", index=False)

    # Player stats for this match
    stats_parser = StatsParser(stats_obj)
    df_stats = stats_parser.parse()
    df_stats.to_parquet(match_dir / "stats.parquet", index=False)

    print(f"Stored match data under {match_dir}")
    return match_dir


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Store match data using link")
    parser.add_argument(
        "-l",
        "--links",
        help="Link of all webpages which need to be parsed",
        nargs="*",
        required=True,
    )
    parser.add_argument(
        "-H",
        "--headless",
        help="Opens google chrome by default.",
        default=False,
        action=argparse.BooleanOptionalAction,
    )

    args = parser.parse_args()
    for link in args.links:
        scrape_and_store_match(link, headless=args.headless)
