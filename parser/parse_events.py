import json
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
import logging
from .references import *

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class EventsDataParser:
    """ """

    def __init__(self, file_path: str):
        """
        :param file_path: Path of events JSON file
        :type file_path: str
        """
        self.file_path = Path(file_path)
        self.raw_data: Dict = None
        self.df_events = None
        self.df_qualifiers = None
        self.match_metadata = {}

        self.load_json()
        self.extract_match_metadata()

    def load_json(self) -> None:
        """Load and parse events JSON file."""
        logger.info(f"Loading JSON from {self.file_path}")
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.raw_data = json.load(f)
            logger.info("JSON loaded successfully")
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

    def extract_match_metadata(self) -> Dict[str, Any]:
        """
        Extract match metadata from raw data.

        Returns:
            Dictionary with match_id, home_team_id, away_team_i d, etc.
        """
        logger.info("Extracting match metadata")

        metadata = {}

        if self.raw_data is not None:
            if "matchInfo" in self.raw_data:
                match_info: Dict = self.raw_data["matchInfo"]

                metadata["match_id"] = match_info.get("id", "")
                metadata["local_date"] = match_info.get("localDate", "")
                metadata["local_time"] = match_info.get("localTime", "")
                metadata["match_week"] = match_info.get("week", "")

                if "competition" in match_info:
                    metadata["competition_id"] = match_info["competition"].get("id", "")
                    metadata["competition_name"] = match_info["competition"].get(
                        "name", ""
                    )
                    metadata["competition_code"] = match_info["competition"].get(
                        "competitionCode", ""
                    )

                if (
                    "tournamentCalendar" in match_info
                    and "name" in match_info["tournamentCalendar"]
                ):
                    metadata["season"] = match_info["tournamentCalendar"]["name"]

                if "contestant" in match_info:
                    contestants = match_info["contestant"]
                    for contestant in contestants:
                        if "position" in contestant:
                            if contestant["position"] == "home":
                                metadata["home_team_id"] = contestant.get("id", "")
                                metadata["home_team_name"] = contestant.get("name", "")
                            elif contestant["position"] == "away":
                                metadata["away_team_name"] = contestant.get("name", "")
                                metadata["away_team_id"] = contestant.get("id", "")
                            else:
                                logger.info(
                                    f"Position doesn't contain home/away: {contestant}"
                                )
                if "venue" in match_info:
                    metadata["venue"] = match_info["venue"].get("shortName", "")
            else:
                logger.error(f"Key `matchInfo` not found in data..")
                raise KeyError(f"Key `matchInfo` not found in data..")

            if (
                "liveData" in self.raw_data
                and "matchDetails" in self.raw_data["liveData"]
            ):
                match_details: Dict = self.raw_data["liveData"]["matchDetails"]

                metadata["winner"] = match_details.get("winner", "")

                if "scores" in match_details and "total" in match_details["scores"]:
                    metadata["goals_home"] = match_details["scores"]["total"].get(
                        "home", ""
                    )
                    metadata["goals_away"] = match_details["scores"]["total"].get(
                        "away", ""
                    )
            else:
                logger.error(f"Key `liveData`/`matchDetails` not found in data..")
                raise KeyError(f"Key liveData`/`matchDetails` not found in data..")
            self.match_metadata = metadata
            return metadata
        else:
            raise Exception("`raw_data` is None")

    def parse_events_and_qualifiers(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Parse raw events into two normalized dataframes:
        1. df_events: One row per event
        2. df_qualifiers: One row per qualifier per event

        Returns:
            Tuple of (df_events, df_qualifiers)
        """
        if "liveData" in self.raw_data and "event" in self.raw_data["liveData"]:
            self.events_raw = self.raw_data["liveData"]["event"]
            logger.info(f"Extracted {len(self.events_raw)} raw events")
        else:
            raise ValueError("Unable to locate events in JSON structure")

        logger.info("Parsing events and qualifiers into separate DataFrames")

        events_list = []
        qualifiers_list = []

        for raw_event in self.events_raw:
            _id = raw_event.get("id")

            # ============================================================
            # Parse main event (SINGLE ROW)
            # ============================================================
            event_record = {
                "id": _id,
                "match_id": self.match_metadata["match_id"],
                "type_id": raw_event.get("typeId"),
                "type_name": OptaEventTypeReference.get_type_name(
                    raw_event.get("typeId")
                ),
                "period_id": raw_event.get("periodId"),
                "minute": raw_event.get("timeMin"),
                "second": raw_event.get("timeSec"),
                "team_id": raw_event.get("contestantId"),
                "player_id": raw_event.get("playerId", None),
                "player_name": raw_event.get("playerName", None),
                "outcome": raw_event.get("outcome"),
                "x": raw_event.get("x"),
                "y": raw_event.get("y"),
                "timestamp": raw_event.get("timeStamp"),
            }
            events_list.append(event_record)

            # ============================================================
            # Parse qualifiers
            # ============================================================
            for qualifier in raw_event.get("qualifier", []):
                qual_id = qualifier.get("qualifierId")
                qual_value = qualifier.get("value")

                qualifier_record = {
                    "event_id": _id,
                    "qualifier_id": qual_id,
                    "qualifier_name": OptaQualifierReference.get_qualifier_name(
                        qual_id
                    ),
                    "qualifier_desc": OptaQualifierReference.get_qualifier_description(
                        qual_id
                    ),
                    "value": qual_value,
                }
                qualifiers_list.append(qualifier_record)

        # Create DataFrames
        self.df_events = pd.DataFrame(events_list)
        self.df_events["timestamp"] = pd.to_datetime(
            self.df_events["timestamp"], format="ISO8601"
        )
        self.df_qualifiers = pd.DataFrame(qualifiers_list)

        logger.info(f"Created df_events: {self.df_events.shape}")
        logger.info(f"Created df_qualifiers: {self.df_qualifiers.shape}")

        return self.df_events, self.df_qualifiers
