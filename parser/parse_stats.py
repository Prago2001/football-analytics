import pandas as pd
import json
import logging
import os
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class StatsParser:
    """
    Parser for extracting player statistics from match data

    Extracts:
    1. matchId from matchInfo
    2. team_id (contestantId) for each team
    3. Player details: playerId, matchName, shirtNumber, position
    4. All player statistics as individual columns
    5. Returns a pandas DataFrame with all data
    """

    def __init__(self, match_data: Dict):
        """
        Initialize the StatsParser with match data

        Args:
            match_data (Dict): The complete match data dictionary
        """
        self.match_data = match_data
        self.match_id = None
        self.teams = {}
        self.all_stats_columns = set()

    def extract_match_id(self) -> str:
        """
        Extract matchId from matchInfo object

        Returns:
            str: The match ID
        """
        try:
            self.match_id = self.match_data["matchInfo"]["id"]
            return self.match_id
        except KeyError as e:
            logger.error(f"Error extracting match ID: {e}")
            return None

    def extract_lineup_data(self) -> pd.DataFrame:
        """
        Parse lineUp array and extract all player data with stats

        Returns:
            pd.DataFrame: DataFrame with all players and their statistics
        """
        all_players = []

        # Extract match ID first
        self.extract_match_id()

        try:
            lineup_array = self.match_data["liveData"]["lineUp"]

            for team_data in lineup_array:
                # Extract team information
                team_id = team_data.get("contestantId")
                self.teams[team_id] = team_data

                # Process each player in the team
                players_list = team_data.get("player", [])

                for player in players_list:
                    # Extract basic player info
                    player_info = {
                        "matchId": self.match_id,
                        "team_id": team_id,
                        "playerId": player.get("playerId"),
                        "matchName": player.get("matchName"),
                        "shirtNumber": player.get("shirtNumber"),
                        "position": player.get("position"),
                    }

                    # Extract all stats
                    stats_list = player.get("stat", [])

                    for stat in stats_list:
                        stat_type = stat.get("type")
                        stat_value = stat.get("value")

                        # Track all stat types
                        self.all_stats_columns.add(stat_type)

                        # Add stat to player info
                        player_info[stat_type] = stat_value

                    all_players.append(player_info)

            # Create DataFrame
            df = pd.DataFrame(all_players)

            # Reorder columns: basic info first, then stats
            basic_columns = [
                "matchId",
                "team_id",
                "playerId",
                "matchName",
                "shirtNumber",
                "position",
            ]
            stat_columns = sorted(list(self.all_stats_columns))
            column_order = basic_columns + stat_columns

            # Ensure all columns exist in the DataFrame
            for col in column_order:
                if col not in df.columns:
                    df[col] = None

            df = df[column_order]

            # Convert stat columns to numeric (handling None/NaN values)
            for col in stat_columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            logger.info(f"Extracted stats of shape {df.shape}")
            return df

        except KeyError as e:
            logger.error(f"Error extracting lineup data: {e}")
            return pd.DataFrame()

    def parse(self) -> pd.DataFrame:
        """
        Main parsing method that orchestrates the extraction

        Returns:
            pd.DataFrame: Complete player statistics dataframe
        """
        df = self.extract_lineup_data()
        return df

    def get_team_ids(self) -> Dict[str, str]:
        """
        Get all team IDs from the match

        Returns:
            Dict[str, str]: Mapping of team_id to team data
        """
        return self.teams

    def get_all_stat_types(self) -> List[str]:
        """
        Get all unique stat types available

        Returns:
            List[str]: Sorted list of all stat types
        """
        return sorted(list(self.all_stats_columns))

    def filter_by_position(self, df: pd.DataFrame, position: str) -> pd.DataFrame:
        """
        Filter players by position

        Args:
            df (pd.DataFrame): The players dataframe
            position (str): Position to filter by (e.g., 'Midfielder', 'Defender')

        Returns:
            pd.DataFrame: Filtered dataframe
        """
        return df[df["position"] == position].copy()

    def filter_by_team(self, df: pd.DataFrame, team_id: str) -> pd.DataFrame:
        """
        Filter players by team ID

        Args:
            df (pd.DataFrame): The players dataframe
            team_id (str): Team ID to filter by

        Returns:
            pd.DataFrame: Filtered dataframe
        """
        return df[df["team_id"] == team_id].copy()

    def get_summary_stats(
        self, df: pd.DataFrame, stat_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get summary statistics for players

        Args:
            df (pd.DataFrame): The players dataframe
            stat_columns (Optional[List[str]]): Specific stats to summarize. If None, uses all numeric columns

        Returns:
            pd.DataFrame: Summary statistics
        """
        if stat_columns is None:
            # Use all numeric columns except the basic info ones
            stat_columns = df.select_dtypes(include=["number"]).columns.tolist()

        return df[["matchName", "position"] + stat_columns].describe()

    @staticmethod
    def load_and_save_stats(
        new_df: pd.DataFrame,
        parquet_path: str = "data/match-stats/stats.parquet",
        append: bool = False,
    ) -> pd.DataFrame:
        """
        Load existing parquet file and optionally append new dataframe

        Args:
            new_df (pd.DataFrame): New dataframe to add (can be None to just load)
            parquet_path (str): Path to the parquet file. Default: 'data/match-stats/stats.parquet'
            append (bool): Whether to append new_df to existing data. Default: False

        Returns:
            pd.DataFrame: Combined or loaded dataframe
        """
        # Ensure directory exists
        directory = os.path.dirname(parquet_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")

        # Load existing parquet file if it exists
        if os.path.exists(parquet_path):
            try:
                existing_df = pd.read_parquet(parquet_path)
                logger.info(f"Loaded existing parquet file: {parquet_path}")
                logger.info(f"Existing dataframe shape: {existing_df.shape}")
            except Exception as e:
                logger.error(f"Error loading parquet file: {e}")
                existing_df = pd.DataFrame()
        else:
            logger.info(
                f"Parquet file not found at {parquet_path}. Will create new file."
            )
            existing_df = pd.DataFrame()

        # Append new data if requested
        if append and new_df is not None and not new_df.empty:
            logger.info(f"Appending new dataframe with shape: {new_df.shape}")

            # Combine dataframes
            if existing_df.empty:
                combined_df = new_df.copy()
                logger.info("No existing data. Using new dataframe as base.")
            else:
                # Check for duplicate matchIds
                existing_match_ids = set(existing_df["matchId"].unique())
                new_match_ids = set(new_df["matchId"].unique())
                duplicate_matches = existing_match_ids.intersection(new_match_ids)

                if duplicate_matches:
                    logger.warning(
                        f"Found {len(duplicate_matches)} duplicate match(es): {duplicate_matches}"
                    )
                    logger.warning(
                        "Removing duplicate matches from existing data before appending"
                    )
                    existing_df = existing_df[
                        ~existing_df["matchId"].isin(duplicate_matches)
                    ]

                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                logger.info(f"Combined dataframe shape: {combined_df.shape}")

            # Save to parquet
            try:
                combined_df.to_parquet(parquet_path, index=False)
                logger.info(f"Successfully saved to parquet: {parquet_path}")
                logger.info(f"Total records in parquet: {len(combined_df)}")
                return combined_df
            except Exception as e:
                logger.error(f"Error saving to parquet: {e}")
                return combined_df

        else:
            if append:
                logger.warning(
                    "Append requested but new_df is None or empty. Returning existing data."
                )
            else:
                logger.info("Append not requested. Returning existing data.")

            return existing_df
