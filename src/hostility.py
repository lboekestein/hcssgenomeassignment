# src/hostility.py
"""
Specifies the function used to compute the hostility index
"""

import numpy as np
import pandas as pd


def compute_hostility_index(
    df: pd.DataFrame,
    episode: "ConflictEpisode",
) -> pd.DataFrame:
    """
    Computes the hostility index for a given conflict episode.

    This function aggregates cooperation and conflict events by direction and week, computing a hostility index
    and event count for each direction.

    Args:
        df (pd.DataFrame): The input DataFrame containing event data.
        episode (ConflictEpisode): The conflict episode for which to compute the hostility index.

    Returns:
        pd.DataFrame: A DataFrame containing the computed hostility index and event counts.
    """

    # filter only on selected episode
    episode_data = df[df["dyad"] == episode.dyad]

    # flip intensity so higher intensity means more hostile
    episode_data["intensity"] = -episode_data["intensity"]

    # aggregate per direction, per week
    directional = (
        episode_data.set_index("event_date")
        .groupby(["direction", pd.Grouper(freq="W")])
        .agg(
            hostility_index=("intensity", "sum"),
            event_count=("intensity", "size"),
        )
        .reset_index()
    )

    # pivot so each direction becomes its own set of columns
    pivoted = directional.pivot(
        index="event_date",
        columns="direction",
        values=["hostility_index", "event_count"],
    )
    # flatten the resulting columns
    pivoted.columns = [f"{metric}_{direction}" for metric, direction in pivoted.columns]
    pivoted = pivoted.fillna(0).reset_index()

    # identify the actual direction labels present for this dyad
    directions = episode_data["direction"].unique().tolist()
    if len(directions) != 2:
        raise ValueError(
            f"Expected exactly 2 directions for {episode.dyad}, got {directions}"
        )

    hostility_cols = [f"hostility_index_{d}" for d in directions]
    count_cols = [f"event_count_{d}" for d in directions]

    # combined ("net") columns across both directions
    pivoted["hostility_index_combined"] = pivoted[hostility_cols].sum(axis=1)
    pivoted["event_count_combined"] = pivoted[count_cols].sum(axis=1)

    # normalized hostility per direction AND for the combined total
    for col_group in directions + ["combined"]:
        h_col = f"hostility_index_{col_group}"
        c_col = f"event_count_{col_group}"
        pivoted[f"normalized_hostility_{col_group}"] = (
            pivoted[h_col] * np.log1p(pivoted[c_col]) / pivoted[c_col].clip(lower=1)
        )

    return pivoted.set_index("event_date")