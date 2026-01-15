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

    def __init__(
        self,
        event_data_object: Dict,
        file_path: str | None = None,
    ):
        self.raw_data: Dict = None
        self.df_events = None
        self.df_qualifiers = None
        self.df_metadata = None
        self.match_metadata = {}

        if file_path is not None:
            self.file_path = Path(file_path)
            self.load_json()
        else:
            self.raw_data = event_data_object
            self.extract_match_metadata()

    def load_json(self) -> None:
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
                metadata["match_status"] = match_details.get("matchStatus", "")

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

    def create_metadata_dataframe(self) -> pd.DataFrame:
        logger.info("Creating metadata DataFrame")
        if not self.match_metadata:
            raise ValueError(
                "Match metadata not extracted. Call extract_match_metadata() first."
            )

        df_metadata = pd.DataFrame([self.match_metadata])
        self.df_metadata = df_metadata
        logger.info(f"Created df_metadata: {self.df_metadata.shape}")
        return df_metadata

    def parse_events_and_qualifiers(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
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

        self.df_events = pd.DataFrame(events_list)
        self.df_events["timestamp"] = pd.to_datetime(
            self.df_events["timestamp"], format="ISO8601"
        )
        self.df_qualifiers = pd.DataFrame(qualifiers_list)

        logger.info(f"Created df_events: {self.df_events.shape}")
        logger.info(f"Created df_qualifiers: {self.df_qualifiers.shape}")
        return self.df_events, self.df_qualifiers

    @staticmethod
    def load_or_append_metadata(
        df_metadata: pd.DataFrame = None, output_dir: str = "data/match-events"
    ) -> pd.DataFrame:
        parquet_path = Path(output_dir) / "metadata.parquet"

        if df_metadata is None:
            if parquet_path.exists():
                logger.info(f"Loading metadata parquet: {parquet_path}")
                df_result = pd.read_parquet(parquet_path)
                logger.info(f"Loaded metadata with {len(df_result)} rows")
                return df_result
            else:
                logger.error(f"No metadata parquet found at: {parquet_path}")
                raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
        else:
            parquet_path.parent.mkdir(parents=True, exist_ok=True)
            if parquet_path.exists():
                logger.info(f"Loading existing metadata parquet: {parquet_path}")
                df_existing = pd.read_parquet(parquet_path)
                df_combined = pd.concat([df_existing, df_metadata], ignore_index=True)
                logger.info(f"Appended new metadata. Total rows: {len(df_combined)}")
            else:
                logger.info(f"Creating new metadata parquet: {parquet_path}")
                df_combined = df_metadata

            df_combined.to_parquet(parquet_path, index=False)
            logger.info(f"Saved metadata parquet with {len(df_combined)} rows")
            return df_combined

    @staticmethod
    def load_or_append_events(
        df_events: pd.DataFrame = None, output_dir: str = "data/match-events"
    ) -> pd.DataFrame:
        parquet_path = Path(output_dir) / "events.parquet"

        if df_events is None:
            if parquet_path.exists():
                logger.info(f"Loading events parquet: {parquet_path}")
                df_result = pd.read_parquet(parquet_path)
                logger.info(f"Loaded events with {len(df_result)} rows")
                return df_result
            else:
                logger.error(f"No events parquet found at: {parquet_path}")
                raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
        else:
            parquet_path.parent.mkdir(parents=True, exist_ok=True)
            if parquet_path.exists():
                logger.info(f"Loading existing events parquet: {parquet_path}")
                df_existing = pd.read_parquet(parquet_path)
                df_combined = pd.concat([df_existing, df_events], ignore_index=True)
                logger.info(f"Appended new events. Total rows: {len(df_combined)}")
            else:
                logger.info(f"Creating new events parquet: {parquet_path}")
                df_combined = df_events

            df_combined.to_parquet(parquet_path, index=False)
            logger.info(f"Saved events parquet with {len(df_combined)} rows")
            return df_combined

    @staticmethod
    def load_or_append_qualifiers(
        df_qualifiers: pd.DataFrame = None, output_dir: str = "data/match-events"
    ) -> pd.DataFrame:
        parquet_path = Path(output_dir) / "qualifiers.parquet"

        if df_qualifiers is None:
            if parquet_path.exists():
                logger.info(f"Loading qualifiers parquet: {parquet_path}")
                df_result = pd.read_parquet(parquet_path)
                logger.info(f"Loaded qualifiers with {len(df_result)} rows")
                return df_result
            else:
                logger.error(f"No qualifiers parquet found at: {parquet_path}")
                raise FileNotFoundError(f"Parquet file not found: {parquet_path}")
        else:
            parquet_path.parent.mkdir(parents=True, exist_ok=True)
            if parquet_path.exists():
                logger.info(f"Loading existing qualifiers parquet: {parquet_path}")
                df_existing = pd.read_parquet(parquet_path)
                df_combined = pd.concat([df_existing, df_qualifiers], ignore_index=True)
                logger.info(f"Appended new qualifiers. Total rows: {len(df_combined)}")
            else:
                logger.info(f"Creating new qualifiers parquet: {parquet_path}")
                df_combined = df_qualifiers

            df_combined.to_parquet(parquet_path, index=False)
            logger.info(f"Saved qualifiers parquet with {len(df_combined)} rows")
            return df_combined
