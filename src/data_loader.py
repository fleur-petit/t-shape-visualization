"""T-Shape Skills Data Loader"""

import pandas as pd
from pathlib import Path
from typing import Tuple


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load T-shape skills data from CSV files.

    Returns:
        Tuple of (content_data, shape_data) DataFrames
    """
    data_dir = Path(__file__).parent.parent / "data"

    # Load skills content data
    content_data = pd.read_csv(data_dir / "t_shape_content.csv", sep=";")

    # Filter out text rows that are not actual skills
    content_data = content_data[~content_data["category"].isin(["Text"])].copy()

    # Convert numeric columns
    content_data["y"] = pd.to_numeric(content_data["y"], errors="coerce")
    content_data["y_aim"] = pd.to_numeric(content_data["y_aim"], errors="coerce")

    # Load T-shape outline data
    shape_data = pd.read_csv(data_dir / "t_shape_shape.csv", sep=";")

    return content_data, shape_data


def get_category_colors() -> dict:
    """Get color mapping for skill categories."""
    return {
        "Domain": "#FF6B6B",  # Red
        "Technical": "#4ECDC4",  # Teal
        "Personal": "#45B7D1",  # Blue
    }


def prepare_skills_for_plotting(content_data: pd.DataFrame) -> pd.DataFrame:
    """Prepare skills data for visualization."""
    # Create position mapping for skills within categories
    plotting_data = content_data.copy()

    # Sort by category and skill level
    plotting_data = plotting_data.sort_values(
        ["category", "y"], ascending=[True, False]
    )

    # Assign x positions based on category
    category_x_positions = {"Domain": 1, "Technical": 2, "Personal": 3}
    plotting_data["x"] = plotting_data["category"].map(category_x_positions)

    return plotting_data
