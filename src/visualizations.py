"""T-Shape Skills Visualisation Functions"""

import polars as pl
from plotnine import (
    ggplot,
    aes,
    geom_polygon,
    geom_label,
    scale_fill_manual,
    labs,
    theme_minimal,
    theme,
    element_text,
)

from src.data_loader import get_category_colors
from collections import defaultdict


def _flip_sign_y(df: pl.DataFrame) -> pl.DataFrame:
    """Flip the sign of all columns containing the letter 'y' in their name."""
    y_cols = [col for col in df.columns if col.startswith("y")]
    return df.with_columns([-pl.col(col) for col in y_cols])


def _get_x_position(y_pos: float, shape_data: pl.DataFrame, y_group: str) -> float:
    """Return a single x position for a skill label based on y_pos and y_group.

    - Divide the width into 3 equal areas.
    - If abs(y_pos) > height_horizontal, width is from 1 to width_horizontal - 1.
    - "Domain": middle of left area.
    - "Technical": middle of plot.
    - "Personal": middle of right area.
    """
    height_horizontal = max(abs(shape_data.filter(pl.col("x") == 0)["y"]))
    width_horizontal = max(shape_data["x"])
    if abs(y_pos) >= height_horizontal:
        x_min = 1
        x_max = width_horizontal - 1
    else:
        x_min = 0
        x_max = width_horizontal

    area_width = (x_max - x_min) / 3

    if y_group == "Domain":
        x_pos = x_min + area_width / 2
    elif y_group == "Technical":
        x_pos = x_min + area_width * 1.5
    elif y_group == "Personal":
        x_pos = x_min + area_width * 2.5

    return x_pos


def _position_skills(
    skills_df: pl.DataFrame,
    y_col: str,
    shape_data: pl.DataFrame,
) -> pl.DataFrame:
    """Position text labels within T-shape boundaries."""

    skills_df = skills_df.with_columns(
        [
            pl.struct(["category", y_col])
            .map_elements(
                lambda row: _get_x_position(row[y_col], shape_data, row["category"]),
                return_dtype=pl.Float64,
            )
            .alias("x_pos"),
            pl.col(y_col).alias("y_pos"),
        ]
    )

    skills_df = _resolve_duplicate_positions(skills_df)

    return skills_df


def _resolve_duplicate_positions(df: pl.DataFrame) -> pl.DataFrame:
    """Recursively adjust y_pos for duplicated (x_pos, y_pos) pairs until all are unique."""

    max_iterations = 10  # Prevent infinite loops
    adjustment = 0.25

    for _ in range(max_iterations):
        # Create a unique key for each (x_pos, y_pos) pair
        keys = (
            df.select(
                pl.concat_str(
                    [pl.col("x_pos").cast(pl.String), pl.col("y_pos").cast(pl.String)],
                    separator="_",
                )
            )
            .to_series()
            .to_list()
        )

        # Count occurrences for each key
        key_counts = defaultdict(int)
        y_pos_adjustments = []

        duplicates_found = False

        for key in keys:
            key_counts[key] += 1
            if key_counts[key] > 1:
                duplicates_found = True
            y_pos_adjustments.append((key_counts[key] - 1) * adjustment)

        # Add the adjustment to y_pos
        df = df.with_columns(
            (pl.col("y_pos") + pl.Series(y_pos_adjustments)).alias("y_pos")
        )

        if not duplicates_found:
            break

    return df


def create_t_shape_visualization(
    content_data: pl.DataFrame, shape_data: pl.DataFrame, mode: str = "current"
) -> object:
    """Create T-shape visualisation using ggplot (plotnine) with text boxes."""
    content_data = _flip_sign_y(content_data)
    shape_data = _flip_sign_y(shape_data)

    # Get colors for categories
    colors = get_category_colors()

    # Prepare T-shape polygon for filling - convert to pandas only for ggplot
    shape_data = shape_data.with_columns(pl.lit(1).alias("group"))

    # Create base plot with filled T-shape
    plot = ggplot() + geom_polygon(
        data=shape_data,
        mapping=aes(x="x", y="y", group="group"),
        fill="lightgray",
        alpha=0.3,
        color="lightgray",
    )

    # Filter and position data based on mode
    if mode == "current":
        # Show only current skills
        positioned_data = _position_skills(content_data, "y", shape_data)

        if len(positioned_data) > 0:
            plot = _plot_skills(plot, colors, positioned_data, label="skill")

    elif mode == "target":
        # Show target skills (data is already filtered to y != y_aim when mode is "target")
        if len(content_data) > 0:
            # Add the absolute difference to the skill label
            target_skills_with_diff = content_data.with_columns(
                (
                    pl.col("skill")
                    + ": +"
                    + (pl.col("y_aim") - pl.col("y")).abs().cast(pl.String)
                ).alias("skill_label")
            )

            positioned_data = _position_skills(
                target_skills_with_diff, "y_aim", shape_data
            )

            plot = _plot_skills(plot, colors, positioned_data, label="skill_label")

    # Add styling
    plot = (
        plot
        + labs(title="T-shape skills profile", x="", y="Skill level", fill="Category")
        + theme_minimal()
        + theme(
            figure_size=(16, 10),  # Make it wider
            plot_title=element_text(size=16, face="bold"),
            axis_title=element_text(size=12),
            legend_title=element_text(size=12),
            axis_text_x=element_text(size=0),  # Hide x-axis labels
            legend_position="none",  # Hide the legend
        )
    )

    return plot


def _plot_skills(plot, colors, positioned_data, label) -> object:
    # Slightly modify y_pos if it is part of a duplicate combination of x_pos and y_pos

    plot = (
        plot
        + geom_label(
            data=positioned_data,
            mapping=aes(x="x_pos", y="y_pos", label=label, fill="category"),
            alpha=0.8,
            size=10,
            color="white",
        )
        + scale_fill_manual(values=colors)
    )
    return plot
