"""T-Shape Skills Data Loader"""

import polars as pl
from pathlib import Path
from typing import Tuple


def load_data() -> Tuple[pl.DataFrame, pl.DataFrame]:
    """Load T-shape skills data from CSV files.

    Returns:
        Tuple of (content_data, shape_data) DataFrames
    """
    data_dir = Path(__file__).parent.parent / "data"

    # Load and preprocess skills content data in one polars pipe
    content_data = pl.read_csv(
        data_dir / "t_shape_content.csv", separator=";"
    ).with_columns(
        [
            (pl.col("y").cast(pl.Float64)),
            (pl.col("y_aim").cast(pl.Float64)),
        ]
    )

    # Load T-shape outline data
    shape_data = pl.read_csv(
        data_dir / "t_shape_shape.csv", separator=";"
    ).with_columns(pl.col("y").cast(pl.Float32))

    return content_data, shape_data


def get_category_colors() -> dict:
    """Get color mapping for skill categories."""
    return {
        "Domain": "#821e7d",  # Purple
        "Technical": "#008cbe",  # Blue
        "Personal": "#7db43c",  # Green
    }
