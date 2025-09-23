"""Shiny App for T-Shape Skills Visualisation"""

from shiny import App, render, ui, reactive
from io import BytesIO
import base64
import polars as pl
from typing import Any, Union

from src.data_loader import load_data
from src.visualizations import (
    create_t_shape_visualization,
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
    ui.layout_sidebar(
        ui.sidebar(
            ui.h3("Options"),
            ui.p(
                "Turn the toggle on to show only the skills that I want to improve upon.",
                class_="text-muted small",
            ),
            ui.input_switch(
                "show_target",
                "Skills marked for growth only",
                value=False,
            ),
            ui.p(
                "Turn the toggle on to show a table with raw data below the t-shape.",
                class_="text-muted small",
            ),
            ui.input_switch("show_raw_data", "Show raw data", value=False),
            ui.hr(),
            ui.h4("Legend"),
            ui.HTML("""
            <div class="legend">
                <p><em>The T-shape goes from 0 to 10 where 10 stands for "I can instruct others." and 0-4 stand for "I am familiar with the basics.".</em></p>
                <p><strong>Skill categories:</strong></p>
                <ul style="list-style: none; padding: 0;">
                    <li><span style="background-color: #821e7d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">Domain</span> Alliander-specific knowledge</li>
                    <li><span style="background-color: #008cbe; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">Technical</span> Technical skills & tools</li>
                    <li><span style="background-color: #7db43c; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px;">Personal</span> Soft skills & competencies</li>
                </ul>
                <p><strong>Display modes:</strong></p>
                <ul style="list-style: none; padding: 0;">
                    <li><strong>Current skills only:</strong> Show current skill levels</li>
                    <li><strong>Skills marked for growth only:</strong> Show only those skills that I want to improve upon</li>
                </ul>
            </div>
            """),
            width=300,
        ),
        ui.div(
            ui.output_ui("main_content"),
        ),
    ),
    # Footer with GitHub link
    ui.div(
        ui.hr(),
        ui.div(
            ui.HTML("""
                <div class="text-center mt-4 mb-3">
                    <a href="https://github.com/fleur-petit/t-shape-visualization" target="_blank" 
                       class="text-decoration-none text-muted">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" 
                             class="bi bi-github me-2" viewBox="0 0 16 16">
                            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.012 8.012 0 0 0 16 8c0-4.42-3.58-8-8-8z"/>
                        </svg>
                        View source on GitHub
                    </a>
                </div>
            """),
            class_="container",
        ),
    ),
)


def server(input: Any, output: Any, session: Any) -> None:
    @reactive.calc
    def filtered_content_data() -> pl.DataFrame:
        """Return filtered content data based on show_target toggle."""
        if not data_loaded:
            return pl.DataFrame()

        if input.show_target():
            # Only show skills where y != y_aim (skills marked for growth)
            return content_data.filter(
                (pl.col("y_aim").is_not_null()) & (pl.col("y") != pl.col("y_aim"))
            )
        else:
            # Show all skills
            return content_data

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
            ui.output_ui("conditional_raw_data"),
            ui.h3("Skills breakdown by category"),
            ui.output_ui("skills_breakdown"),
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
        fig = create_t_shape_visualization(filtered_content_data(), shape_data, mode)

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
    def raw_data_table() -> Union[pl.DataFrame, Any]:
        if not data_loaded:
            return pl.DataFrame()
        # Return filtered polars DataFrame directly
        return render.DataGrid(filtered_content_data(), width="100%")

    @render.ui
    def skills_breakdown() -> ui.Tag:
        if not data_loaded:
            return ui.div("Data not available")

        # Get filtered data
        data_to_use = filtered_content_data()

        # Get unique categories using polars
        categories = data_to_use.select("category").unique().to_series().to_list()

        tabs = []
        for cat in categories:
            # Filter and sort data using polars
            cat_data = data_to_use.filter(pl.col("category") == cat).sort(
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
