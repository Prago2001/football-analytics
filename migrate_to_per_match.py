"""One-time migration: split the consolidated parquets in data/match-events
and data/match-stats into per-match directories under data/matches/.

Usage:
    python migrate_to_per_match.py

The script is idempotent – re-running it will overwrite previously migrated
files for matches that are already present, but will not delete any data.
"""

import re
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths – all relative to the repo root
# ---------------------------------------------------------------------------
EVENTS_DIR = Path("data/match-events")
STATS_DIR = Path("data/match-stats")
OUT_DIR = Path("data/matches")

EVENTS_PARQUET = EVENTS_DIR / "events.parquet"
QUALIFIERS_PARQUET = EVENTS_DIR / "qualifiers.parquet"
METADATA_PARQUET = EVENTS_DIR / "metadata.parquet"
STATS_PARQUET = STATS_DIR / "stats.parquet"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _slug(value: str) -> str:
    """Filesystem-safe slug: non-alphanumeric chars → hyphens, lowercased."""
    value = re.sub(r"[^A-Za-z0-9]+", "-", str(value).strip())
    return value.strip("-").lower() or "unknown"


def _match_dir(row: pd.Series, base_dir: Path = OUT_DIR) -> Path:
    """Build the per-match directory path from a metadata row."""
    competition = (
        row.get("competition_code") or row.get("competition_name") or "competition"
    )
    home = row.get("home_team_name") or "home"
    away = row.get("away_team_name") or "away"
    date_str = str(row.get("local_date") or "")
    date_token = date_str[:10] if date_str else "unknown-date"

    folder = f"{_slug(competition)}_{_slug(home)}_{_slug(away)}_{_slug(date_token)}"
    match_dir = base_dir / folder
    match_dir.mkdir(parents=True, exist_ok=True)
    return match_dir


# ---------------------------------------------------------------------------
# Main migration
# ---------------------------------------------------------------------------
def migrate(
    events_path: Path = EVENTS_PARQUET,
    qualifiers_path: Path = QUALIFIERS_PARQUET,
    metadata_path: Path = METADATA_PARQUET,
    stats_path: Path = STATS_PARQUET,
    out_dir: Path = OUT_DIR,
) -> None:
    """Read the consolidated parquets and write per-match parquet files.

    Args:
        events_path: Path to the consolidated events parquet.
        qualifiers_path: Path to the consolidated qualifiers parquet.
        metadata_path: Path to the consolidated metadata parquet (one row per match).
        stats_path: Path to the consolidated stats parquet.
        out_dir: Root directory under which per-match folders are created.
    """
    # ---- Load all consolidated dataframes --------------------------------
    print("Loading consolidated parquets...")

    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata parquet not found: {metadata_path}")
    df_meta = pd.read_parquet(metadata_path)
    print(f"  metadata: {len(df_meta)} rows ({df_meta['match_id'].nunique()} matches)")

    df_events = pd.read_parquet(events_path) if events_path.exists() else pd.DataFrame()
    print(f"  events  : {len(df_events)} rows")

    df_quals = (
        pd.read_parquet(qualifiers_path) if qualifiers_path.exists() else pd.DataFrame()
    )
    print(f"  qualifiers: {len(df_quals)} rows")

    df_stats = pd.read_parquet(stats_path) if stats_path.exists() else pd.DataFrame()
    print(f"  stats   : {len(df_stats)} rows")

    # ---- Build event_id → match_id lookup (from events) ------------------
    # events.parquet contains match_id directly; qualifiers join via event_id
    if (
        not df_events.empty
        and "match_id" in df_events.columns
        and "id" in df_events.columns
    ):
        event_to_match = df_events.set_index("id")["match_id"].to_dict()
    else:
        event_to_match = {}

    # Attach match_id to qualifiers if not already present
    if not df_quals.empty and "match_id" not in df_quals.columns:
        if event_to_match:
            df_quals = df_quals.copy()
            df_quals["match_id"] = df_quals["event_id"].map(event_to_match)
        else:
            df_quals["match_id"] = None

    # ---- Attach match_id to stats if not already present -----------------
    # stats.parquet may have 'match_id' or it may need deriving
    # (StatsParser already writes match_id; handle the case where it does not)
    if not df_stats.empty and "matchId" not in df_stats.columns:
        print(
            "  WARNING: stats parquet has no match_id column – "
            "stats will not be split by match."
        )

    # ---- Write per-match files -------------------------------------------
    print(f"\nMigrating {len(df_meta)} matches to {out_dir}/...")
    migrated = 0
    for _, meta_row in df_meta.iterrows():
        match_id = meta_row.get("match_id")
        if not match_id:
            print(f"  SKIP: metadata row with no match_id: {meta_row.to_dict()}")
            continue

        match_dir = _match_dir(meta_row, base_dir=out_dir)

        # metadata (single row)
        pd.DataFrame([meta_row]).to_parquet(match_dir / "metadata.parquet", index=False)

        # events
        if not df_events.empty:
            m_events = df_events[df_events["match_id"] == match_id]
            m_events.to_parquet(match_dir / "events.parquet", index=False)
        else:
            pd.DataFrame().to_parquet(match_dir / "events.parquet", index=False)

        # qualifiers
        if not df_quals.empty:
            m_quals = df_quals[df_quals["match_id"] == match_id]
            m_quals.to_parquet(match_dir / "qualifiers.parquet", index=False)
        else:
            pd.DataFrame().to_parquet(match_dir / "qualifiers.parquet", index=False)

        # stats (filter by match_id if the column exists)
        if not df_stats.empty:
            if "matchId" in df_stats.columns:
                m_stats = df_stats[df_stats["matchId"] == match_id]
            else:
                m_stats = pd.DataFrame()
            m_stats.to_parquet(match_dir / "stats.parquet", index=False)
        else:
            pd.DataFrame().to_parquet(match_dir / "stats.parquet", index=False)

        print(f"  [{migrated + 1}/{len(df_meta)}] {match_dir.name}")
        migrated += 1

    print(f"\nDone. Migrated {migrated} matches → {out_dir}")


if __name__ == "__main__":
    migrate()
