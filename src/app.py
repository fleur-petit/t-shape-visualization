"""Shiny App for T-Shape Skills Visualization"""

from shiny import App, render, ui
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from src.data_loader import load_data
from src.visualizations import (
    create_matplotlib_visualization,
    create_plotly_visualization,
    create_skills_summary,
)


# Load data once at startup
try:
    content_data, shape_data = load_data()
    data_loaded = True
    error_message = None
except Exception as e:
    data_loaded = False
    error_message = str(e)


app_ui = ui.page_fluid(
    ui.div(
        ui.h1("📊 T-Shape Skills Visualization", class_="text-center mb-4"),
        ui.p(
            "Interactive visualization of your T-shaped skills profile",
            class_="text-center text-muted mb-5",
        ),
        class_="container",
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("Visualization Options"),
            ui.input_select(
                "viz_type",
                "Choose visualization type:",
                choices={
                    "plotly": "Plotly (Interactive)",
                    "matplotlib": "Matplotlib (Static)",
                },
                selected="plotly",
            ),
            ui.input_checkbox("show_summary", "Show Skills Summary", value=True),
            ui.input_checkbox("show_raw_data", "Show Raw Data", value=False),
            ui.hr(),
            ui.h4("Legend"),
            ui.HTML("""
            <div class="legend">
                <p><strong>Skill Categories:</strong></p>
                <ul style="list-style: none; padding: 0;">
                    <li><span style="color: #FF6B6B; font-size: 16px;">●</span> <strong>Domain:</strong> Alliander-specific knowledge</li>
                    <li><span style="color: #4ECDC4; font-size: 16px;">●</span> <strong>Technical:</strong> Technical skills & tools</li>
                    <li><span style="color: #45B7D1; font-size: 16px;">●</span> <strong>Personal:</strong> Soft skills & competencies</li>
                </ul>
                <p><strong>Markers:</strong></p>
                <ul style="list-style: none; padding: 0;">
                    <li>● Current skill level</li>
                    <li>✕ Target skill level</li>
                </ul>
            </div>
            """),
            width=300,
        ),
        ui.div(
            ui.output_ui("main_content"),
        ),
    ),
)


def server(input, output, session):
    @render.ui
    def main_content():
        if not data_loaded:
            return ui.div(
                ui.h2("❌ Error Loading Data", class_="text-danger"),
                ui.div(f"Error: {error_message}", class_="alert alert-danger"),
                ui.p(
                    "Make sure the data files exist in the 'data' directory.",
                    class_="text-muted",
                ),
                class_="text-center",
            )

        return ui.div(
            ui.h2("Skills Profile Visualization"),
            ui.output_ui("main_plot"),
            ui.br(),
            ui.output_ui("conditional_summary"),
            ui.output_ui("conditional_raw_data"),
            ui.h3("Skills Breakdown by Category"),
            ui.output_ui("skills_breakdown"),
        )

    @render.ui
    def conditional_summary():
        if not data_loaded or not input.show_summary():
            return ui.div()
        return ui.div(
            ui.h3("Skills Summary by Category"), ui.output_data_frame("summary_table")
        )

    @render.ui
    def conditional_raw_data():
        if not data_loaded or not input.show_raw_data():
            return ui.div()
        return ui.div(ui.h3("Raw Skills Data"), ui.output_data_frame("raw_data_table"))

    @render.ui
    def main_plot():
        if not data_loaded:
            return ui.div("Data not available", class_="alert alert-warning")

        if input.viz_type() == "plotly":
            fig = create_plotly_visualization(content_data, shape_data)
            return ui.HTML(fig.to_html(include_plotlyjs="cdn"))
        else:
            fig = create_matplotlib_visualization(content_data, shape_data)

            # Convert matplotlib figure to base64 image
            buffer = BytesIO()
            fig.savefig(buffer, format="png", bbox_inches="tight", dpi=150)
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()
            plt.close(fig)

            return ui.HTML(
                f'<img src="data:image/png;base64,{img_base64}" style="max-width: 100%; height: auto;" />'
            )

    @render.data_frame
    def summary_table():
        if not data_loaded:
            return pd.DataFrame()
        return render.DataGrid(create_skills_summary(content_data), width="100%")

    @render.data_frame
    def raw_data_table():
        if not data_loaded:
            return pd.DataFrame()
        return render.DataGrid(content_data, width="100%")

    @render.ui
    def skills_breakdown():
        if not data_loaded:
            return ui.div("Data not available")

        categories = content_data["category"].unique()

        tabs = []
        for cat in categories:
            cat_data = content_data[content_data["category"] == cat].sort_values(
                "y", ascending=False
            )

            skills_content = []
            for _, row in cat_data.iterrows():
                current = row["y"]
                target = row["y_aim"] if not pd.isna(row["y_aim"]) else None

                target_display = ""
                if target is not None:
                    delta = target - current
                    badge_class = "success" if delta >= 0 else "warning"
                    target_display = f'<span class="badge bg-{badge_class}">Target: {target} ({delta:+.1f})</span>'
                else:
                    target_display = '<span class="text-muted">—</span>'

                skill_html = f"""
                <div class="skill-row mb-2 p-2" style="border: 1px solid #dee2e6; border-radius: 4px;">
                    <div class="row">
                        <div class="col-md-6">
                            <strong>{row["skill"]}</strong>
                        </div>
                        <div class="col-md-3 text-center">
                            <span class="badge bg-primary">Current: {current}</span>
                        </div>
                        <div class="col-md-3 text-center">
                            {target_display}
                        </div>
                    </div>
                </div>
                """
                skills_content.append(skill_html)

            tab_content = ui.div(
                ui.h4(f"{cat} Skills ({len(cat_data)} skills)"),
                ui.HTML("".join(skills_content)),
                class_="mt-3",
            )

            tabs.append(
                ui.nav_panel(f"{cat} ({len(cat_data)})", tab_content, value=cat)
            )

        return ui.navset_tab(*tabs, id="skills_tabs")


app = App(app_ui, server)


def main():
    """Run the Shiny application."""
    app.run()


if __name__ == "__main__":
    main()
