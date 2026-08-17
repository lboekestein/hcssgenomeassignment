# src/episodes.py
"""
Contains a class to define conflict episodes, and defines two example episodes.
"""

from typing import Optional

import pandas as pd


class ConflictEpisode:
    """
    Represents a conflict episode between two parties.

    Attributes:
        partyA (str): The name of the first party.
        partyB (str): The name of the second party.
        label (str): A label for the episode.
        onset_date (pd.Timestamp): The start date of the episode.
        end_date (Optional[pd.Timestamp]): The end date of the episode, if applicable.
    """

    def __init__(
        self,
        partyA: str,
        partyB: str,
        label: str,
        onset_date: pd.Timestamp,
        end_date: Optional[pd.Timestamp] = None,
    ):
        self.partyA = partyA
        self.partyB = partyB
        self.label = label
        self.onset_date = onset_date
        self.end_date = end_date
        self.ongoing = False if end_date else True
        self.dyad = "_".join(sorted(list([partyA, partyB])))


# ----------------
# Example episodes
# ----------------
USA_Iran = ConflictEpisode(
    partyA="usa",
    partyB="iran",
    label="2026 US-Iran War",
    onset_date=pd.Timestamp("2026-02-28"),
)

Israel_Lebanon = ConflictEpisode(
    partyA="israel",
    partyB="lebanon",
    label="2024 Israel-Lebanon War",
    onset_date=pd.Timestamp("2024-09-23"),
    end_date=pd.Timestamp("2024-10-27"),
)

ALL_EPISODES = [USA_Iran, Israel_Lebanon]
