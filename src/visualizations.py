"""T-Shape Skills Visualization Functions"""

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from src.data_loader import get_category_colors


def create_matplotlib_visualization(
    content_data: pd.DataFrame, shape_data: pd.DataFrame
) -> plt.Figure:
    """Create T-shape visualization using matplotlib."""
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot T-shape outline
    ax.plot(
        shape_data["x"], shape_data["y"], "k-", linewidth=2, alpha=0.3, label="T-Shape"
    )

    # Get colors for categories
    colors = get_category_colors()

    # Plot current skills
    for category in content_data["category"].unique():
        category_data = content_data[content_data["category"] == category]
        category_x_positions = {"Domain": 0.5, "Technical": 2.5, "Personal": 4.5}
        x_pos = category_x_positions.get(category, 2.5)

        # Add some jitter to x position for better visibility
        x_positions = [
            x_pos + np.random.uniform(-0.2, 0.2) for _ in range(len(category_data))
        ]

        ax.scatter(
            x_positions,
            category_data["y"],
            c=colors.get(category, "gray"),
            s=60,
            alpha=0.7,
            label=f"{category} (Current)",
        )

    # Plot target skills if they exist
    if "y_aim" in content_data.columns:
        for category in content_data["category"].unique():
            category_data = content_data[content_data["category"] == category]
            category_data = category_data.dropna(subset=["y_aim"])

            if not category_data.empty:
                category_x_positions = {
                    "Domain": 0.5,
                    "Technical": 2.5,
                    "Personal": 4.5,
                }
                x_pos = category_x_positions.get(category, 2.5)
                x_positions = [
                    x_pos + np.random.uniform(-0.2, 0.2)
                    for _ in range(len(category_data))
                ]

                ax.scatter(
                    x_positions,
                    category_data["y_aim"],
                    c=colors.get(category, "gray"),
                    s=60,
                    alpha=0.4,
                    marker="x",
                    label=f"{category} (Target)",
                )

    ax.set_xlabel("Skill Categories")
    ax.set_ylabel("Skill Level")
    ax.set_title("T-Shape Skills Profile")
    ax.legend()
    ax.grid(True, alpha=0.3)

    return fig


def create_plotly_visualization(
    content_data: pd.DataFrame, shape_data: pd.DataFrame
) -> go.Figure:
    """Create interactive T-shape visualization using plotly."""
    fig = go.Figure()

    # Add T-shape outline
    fig.add_trace(
        go.Scatter(
            x=shape_data["x"],
            y=shape_data["y"],
            mode="lines",
            line=dict(color="black", width=2),
            opacity=0.3,
            name="T-Shape Outline",
            hoverinfo="skip",
        )
    )

    # Get colors for categories
    colors = get_category_colors()

    # Add current skills
    for category in content_data["category"].unique():
        category_data = content_data[content_data["category"] == category]
        category_x_positions = {"Domain": 0.5, "Technical": 2.5, "Personal": 4.5}
        x_pos = category_x_positions.get(category, 2.5)

        # Add some jitter to x position
        x_positions = [
            x_pos + np.random.uniform(-0.2, 0.2) for _ in range(len(category_data))
        ]

        fig.add_trace(
            go.Scatter(
                x=x_positions,
                y=category_data["y"],
                mode="markers",
                marker=dict(color=colors.get(category, "gray"), size=10, opacity=0.7),
                name=f"{category} (Current)",
                text=category_data["skill"],
                hovertemplate="<b>%{text}</b><br>Level: %{y}<br>Category: "
                + category
                + "<extra></extra>",
            )
        )

    # Add target skills if they exist
    if "y_aim" in content_data.columns:
        for category in content_data["category"].unique():
            category_data = content_data[content_data["category"] == category]
            category_data = category_data.dropna(subset=["y_aim"])

            if not category_data.empty:
                category_x_positions = {
                    "Domain": 0.5,
                    "Technical": 2.5,
                    "Personal": 4.5,
                }
                x_pos = category_x_positions.get(category, 2.5)
                x_positions = [
                    x_pos + np.random.uniform(-0.2, 0.2)
                    for _ in range(len(category_data))
                ]

                fig.add_trace(
                    go.Scatter(
                        x=x_positions,
                        y=category_data["y_aim"],
                        mode="markers",
                        marker=dict(
                            color=colors.get(category, "gray"),
                            size=10,
                            opacity=0.4,
                            symbol="x",
                        ),
                        name=f"{category} (Target)",
                        text=category_data["skill"],
                        hovertemplate="<b>%{text}</b><br>Target Level: %{y}<br>Category: "
                        + category
                        + "<extra></extra>",
                    )
                )

    fig.update_layout(
        title="Interactive T-Shape Skills Profile",
        xaxis_title="Skill Categories",
        yaxis_title="Skill Level",
        hovermode="closest",
        width=800,
        height=600,
        xaxis=dict(
            tickmode="array",
            tickvals=[0.5, 2.5, 4.5],
            ticktext=["Domain", "Technical", "Personal"],
        ),
    )

    return fig


def create_skills_summary(content_data: pd.DataFrame) -> pd.DataFrame:
    """Create summary statistics for skills by category."""
    summary = (
        content_data.groupby("category")
        .agg({"y": ["count", "mean", "max"], "y_aim": ["mean", "max"]})
        .round(2)
    )

    # Flatten column names
    summary.columns = [
        f"{col[1]}_{col[0]}" if col[1] else col[0] for col in summary.columns
    ]
    summary = summary.reset_index()

    return summary
