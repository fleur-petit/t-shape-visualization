# T-Shape Skills Visualization

Visualization tool for analyzing and exploring T-shaped skills data.

## Features

- 📈 **Static Visualizations**: Plotnine charts for presentations
- 📋 **Skills Summary**: Statistical overview by category
- 🎯 **Target Tracking**: Compare current skills with target levels
- 🔍 **Detailed Breakdown**: Category-wise skill exploration
- 🌐 **Modern Web Interface**: Built with Shiny for Python

## Installation

This project uses [UV](https://docs.astral.sh/uv/) for dependency management. 

1. **Install UV** (if not already installed):
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone and set up the project**:
   ```bash
   cd t-shape-visualization
   uv sync
   ```

## Usage

### Run the Shiny App

```bash
uv run python src/app.py
```

This will start the interactive web application at `http://127.0.0.1:8000`

### Data Format

The application expects two CSV files in the `data/` directory:

1. **`t_shape_content.csv`**: Skills data with columns:
   - `skill`: Skill name
   - `category`: Category (Domain/Technical/Personal)
   - `y`: Current skill level (0-10)
   - `y_aim`: Target skill level (optional)

2. **`t_shape_shape.csv`**: T-shape outline coordinates:
   - `x`: X coordinates for the T-shape
   - `y`: Y coordinates for the T-shape

## Project Structure

```
t-shape-visualization/
├── src/
│   ├── __init__.py
│   ├── app.py              # Main Shiny application
│   ├── data_loader.py      # Data loading and preprocessing
│   └── visualizations.py  # Visualization functions
├── data/
│   ├── t_shape_content.csv # Skills data
│   └── t_shape_shape.csv   # T-shape outline
├── pyproject.toml          # Project configuration
├── uv.lock                 # Dependency lock file
└── README.md
```

## Visualization Types

1. **Interactive Plotly Charts**: 
   - Hover over points to see skill details
   - Zoom and pan capabilities
   - Legend interaction

2. **Static Matplotlib Charts**:
   - Publication-ready plots
   - Customizable styling

## Shiny Framework

This application uses [Shiny for Python](https://shiny.posit.co/py/) which provides:

- **Reactive Programming**: Automatic updates when inputs change
- **Modern UI**: Bootstrap-based responsive interface
- **Fast Performance**: Built on FastAPI/Starlette
- **Easy Deployment**: Can be deployed to various platforms

## Development

### Adding Dependencies

```bash
uv add package-name
```

### Development Dependencies

```bash
uv add --dev pytest black flake8 mypy
```

### Running Tests

```bash
uv run pytest
```

## Customization

- **Colors**: Modify category colors in `src/data_loader.py`
- **Layout**: Adjust chart layouts in `src/visualizations.py`
- **UI**: Customize the Shiny interface in `src/app.py`

## Deployment

The Shiny app can be deployed to:
- **Posit Connect**: Professional deployment platform
- **ShinyApps.io**: Free hosting for Shiny applications
- **Docker**: Container-based deployment
- **Cloud platforms**: AWS, Google Cloud, Azure