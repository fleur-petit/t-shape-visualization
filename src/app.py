"""Shiny App for T-Shape Skills Visualisation"""

from shiny import App, render, ui
from io import BytesIO
import base64
import polars as pl
from typing import Any, Union

from src.data_loader import load_data
from src.visualizations import (
    create_ggplot_visualization,
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
        ui.h1("📊 T-shape skills visualisation", class_="text-center mb-4"),
        ui.p(
            "Interactive visualisation of your T-shaped skills profile",
            class_="text-center text-muted mb-5",
        ),
        class_="container",
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("Visualisation options"),
            ui.input_switch(
                "show_target",
                "Skills marked for growth only",
                value=False,
            ),
            ui.p(
                "Toggle off to show current skills only, or on to show skills marked for growth only.",
                class_="text-muted small",
            ),
            ui.hr(),
            ui.h3("View data"),
            ui.input_checkbox("show_summary", "Show skills summary", value=True),
            ui.input_checkbox("show_raw_data", "Show raw data", value=False),
            ui.hr(),
            ui.h4("Legend"),
            ui.HTML("""
            <div class="legend">
                <p><strong>Skill categories:</strong></p>
                <ul style="list-style: none; padding: 0;">
                    <li><span style="background-color: #821e7d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">Domain</span> Alliander-specific knowledge</li>
                    <li><span style="background-color: #008cbe; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">Technical</span> Technical skills & tools</li>
                    <li><span style="background-color: #7db43c; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">Personal</span> Soft skills & competencies</li>
                </ul>
                <p><strong>Display modes:</strong></p>
                <ul style="list-style: none; padding: 0;">
                    <li><strong>Current skills only:</strong> Show current skill levels as text boxes</li>
                    <li><strong>Skills marked for growth only:</strong> Show only target levels for skills that differ from current</li>
                </ul>
                <p><em>The T-shape goes from 0 to 10 where 10 stands for "I can instruct others." and 0-4 stand for "I am familiar with the basics.".</em></p>
            </div>
            """),
            width=300,
        ),
        ui.div(
            ui.output_ui("main_content"),
        ),
    ),
)


def server(input: Any, output: Any, session: Any) -> None:
    @render.ui
    def main_content() -> ui.Tag:
        if not data_loaded:
            return ui.div(
                ui.h2("❌ Error loading data", class_="text-danger"),
                ui.div(f"Error: {error_message}", class_="alert alert-danger"),
                ui.p(
                    "Make sure the data files exist in the 'data' directory.",
                    class_="text-muted",
                ),
                class_="text-center",
            )

        return ui.div(
            ui.h2("Skills profile visualisation"),
            ui.output_ui("main_plot"),
            ui.br(),
            ui.output_ui("conditional_summary"),
            ui.output_ui("conditional_raw_data"),
            ui.h3("Skills breakdown by category"),
            ui.output_ui("skills_breakdown"),
        )

    @render.ui
    def conditional_summary() -> ui.Tag:
        if not data_loaded or not input.show_summary():
            return ui.div()
        return ui.div(
            ui.h3("Skills summary by category"), ui.output_data_frame("summary_table")
        )

    @render.ui
    def conditional_raw_data() -> ui.Tag:
        if not data_loaded or not input.show_raw_data():
            return ui.div()
        return ui.div(ui.h3("Raw skills data"), ui.output_data_frame("raw_data_table"))

    @render.ui
    def main_plot() -> ui.Tag:
        if not data_loaded:
            return ui.div("Data not available", class_="alert alert-warning")

        # Determine mode based on toggle switch
        mode = "target" if input.show_target() else "current"

        # Use ggplot visualisation with selected mode
        fig = create_ggplot_visualization(content_data, shape_data, mode)

        # Convert ggplot figure to base64 image
        buffer = BytesIO()
        fig.save(buffer, format="png", dpi=200, verbose=False)
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()

        return ui.HTML(
            f'<img src="data:image/png;base64,{img_base64}" style="width: 100%; height: auto; display: block;" />'
        )

    @render.data_frame
    def summary_table() -> Union[pl.DataFrame, Any]:
        if not data_loaded:
            return pl.DataFrame()
        # Return polars DataFrame directly
        summary_df = create_skills_summary(content_data)
        return render.DataGrid(summary_df, width="100%")

    @render.data_frame
    def raw_data_table() -> Union[pl.DataFrame, Any]:
        if not data_loaded:
            return pl.DataFrame()
        # Return polars DataFrame directly
        return render.DataGrid(content_data, width="100%")

    @render.ui
    def skills_breakdown() -> ui.Tag:
        if not data_loaded:
            return ui.div("Data not available")

        # Get unique categories using polars
        categories = content_data.select("category").unique().to_series().to_list()

        tabs = []
        for cat in categories:
            # Filter and sort data using polars
            cat_data = content_data.filter(pl.col("category") == cat).sort(
                "y", descending=True
            )

            skills_content = []
            # Iterate through polars DataFrame rows
            for row in cat_data.iter_rows(named=True):
                current = row["y"]
                target = row["y_aim"] if row["y_aim"] is not None else None

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
                ui.h4(f"{cat} skills ({len(cat_data)} skills)"),
                ui.HTML("".join(skills_content)),
                class_="mt-3",
            )

            tabs.append(
                ui.nav_panel(f"{cat} ({len(cat_data)})", tab_content, value=cat)
            )

        return ui.navset_tab(*tabs, id="skills_tabs")


app = App(app_ui, server)


def main() -> None:
    """Run the Shiny application."""
    app.run()


if __name__ == "__main__":
    main()
