# dash_gallery.py

"""
Paloma's Orrery - Dash Web Gallery

A lightweight Dash web application that serves interactive Plotly
visualizations from a local folder or Google Drive. Designed to be
embedded in or linked from Tony's Google Sites page.

Usage:
    python dash_gallery.py                    # Run locally on port 8050
    python dash_gallery.py --port 8080        # Custom port
    python dash_gallery.py --folder ./dash    # Custom data folder

Dependencies:
    pip install dash plotly

The app reads gallery_metadata.json and figure JSON files from the
data folder. These are produced by dash_converter.py.

Author: Tony Quintanilla / Paloma's Orrery
"""

import os
import sys
import json
import argparse
from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.graph_objects as go
import plotly.io as pio


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_DATA_FOLDER = "dash"
METADATA_FILE = "gallery_metadata.json"
APP_TITLE = "Paloma's Orrery"
APP_SUBTITLE = "Interactive Astronomical Visualizations"

# Color palette - dark theme matching Plotly space visualizations
COLORS = {
    "bg_primary": "#0a0a0f",        # Deep space black
    "bg_secondary": "#12121a",      # Card background
    "bg_tertiary": "#1a1a2e",       # Hover/active state
    "accent": "#c9a84c",            # Gold accent (warm, astronomical)
    "accent_dim": "#8a7535",         # Dimmed gold
    "text_primary": "#e8e6e3",      # Off-white text
    "text_secondary": "#9a9a9a",    # Muted text
    "text_dim": "#5a5a6a",          # Very dim text
    "border": "#2a2a3a",            # Subtle borders
    "category_solar": "#f4a261",    # Solar system - warm orange
    "category_inner": "#e76f51",    # Inner planets - red-orange
    "category_outer": "#2a9d8f",    # Outer planets - teal
    "category_missions": "#264653", # Missions - dark teal
    "category_sgr": "#9b59b6",      # Galactic center - purple
    "category_stellar": "#3498db",  # Stellar - blue
    "category_exo": "#1abc9c",      # Exoplanets - aqua
    "category_climate": "#27ae60",  # Earth system - green
    "category_other": "#7f8c8d",    # Other - grey
}

CATEGORY_COLORS = {
    "solar_system": COLORS["category_solar"],
    "inner_planets": COLORS["category_inner"],
    "outer_planets": COLORS["category_outer"],
    "missions": COLORS["category_missions"],
    "sgr_a": COLORS["category_sgr"],
    "stellar": COLORS["category_stellar"],
    "exoplanets": COLORS["category_exo"],
    "climate": COLORS["category_climate"],
    "other": COLORS["category_other"],
}


# ============================================================================
# DATA LOADING
# ============================================================================

def load_metadata(data_folder):
    """Load gallery metadata from JSON file."""
    metadata_path = os.path.join(data_folder, METADATA_FILE)
    if not os.path.exists(metadata_path):
        return {"visualizations": [], "last_updated": "", "total_count": 0}

    with open(metadata_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_figure(data_folder, filename):
    """Load a Plotly figure from JSON file."""
    filepath = os.path.join(data_folder, filename)
    if not os.path.exists(filepath):
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        fig_dict = json.load(f)

    # Strip the embedded Plotly template to avoid version mismatches
    # (e.g., heatmapgl exists in newer Plotly but not older versions).
    # We apply our own dark theme anyway, so the template is not needed.
    if "layout" in fig_dict and "template" in fig_dict["layout"]:
        del fig_dict["layout"]["template"]

    fig = go.Figure(fig_dict)

    # Apply dark theme overrides for web display
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=COLORS["text_primary"],
        margin=dict(l=10, r=10, t=40, b=10),
    )

    return fig


def get_welcome_figure():
    """Create a placeholder figure for the landing page."""
    fig = go.Figure()
    fig.add_annotation(
        text="Select a visualization from the gallery",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=18, color=COLORS["text_secondary"]),
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig


# ============================================================================
# APP LAYOUT
# ============================================================================

def create_layout(metadata):
    """Build the Dash app layout."""
    visualizations = metadata.get("visualizations", [])
    total = metadata.get("total_count", len(visualizations))
    last_updated = metadata.get("last_updated", "")

    # Group by category
    categories = {}
    for viz in visualizations:
        cat = viz.get("category", "other")
        cat_label = viz.get("category_label", "Other")
        if cat not in categories:
            categories[cat] = {"label": cat_label, "items": []}
        categories[cat]["items"].append(viz)

    # Build gallery cards
    gallery_items = []
    for cat_key, cat_data in categories.items():
        cat_color = CATEGORY_COLORS.get(cat_key, COLORS["category_other"])

        # Category header
        gallery_items.append(
            html.Div(
                html.Span(cat_data["label"], style={
                    "color": cat_color,
                    "fontSize": "0.75rem",
                    "fontWeight": "600",
                    "letterSpacing": "0.1em",
                    "textTransform": "uppercase",
                }),
                style={
                    "padding": "20px 0 8px 0",
                    "borderBottom": f"1px solid {cat_color}33",
                    "marginBottom": "12px",
                }
            )
        )

        # Visualization cards in this category
        for viz in cat_data["items"]:
            viz_id = viz.get("id", "")
            title = viz.get("title", "Untitled")
            desc = viz.get("description", "")
            size = viz.get("size_kb", 0)

            card = html.Div(
                [
                    html.Div(title, style={
                        "fontSize": "0.9rem",
                        "fontWeight": "500",
                        "color": COLORS["text_primary"],
                        "marginBottom": "4px",
                        "lineHeight": "1.3",
                    }),
                    html.Div(desc, style={
                        "fontSize": "0.75rem",
                        "color": COLORS["text_secondary"],
                        "lineHeight": "1.4",
                    }) if desc else None,
                    html.Div(f"{size:.0f} KB", style={
                        "fontSize": "0.65rem",
                        "color": COLORS["text_dim"],
                        "marginTop": "4px",
                    }),
                ],
                id={"type": "viz-card", "index": viz_id},
                n_clicks=0,
                style={
                    "padding": "12px 16px",
                    "cursor": "pointer",
                    "borderRadius": "6px",
                    "border": f"1px solid {COLORS['border']}",
                    "marginBottom": "8px",
                    "transition": "all 0.2s ease",
                    "backgroundColor": COLORS["bg_secondary"],
                },
            )
            gallery_items.append(card)

    # Empty state
    if not visualizations:
        gallery_items.append(
            html.Div(
                [
                    html.Div("No visualizations yet", style={
                        "color": COLORS["text_secondary"],
                        "fontSize": "0.9rem",
                        "marginBottom": "8px",
                    }),
                    html.Div(
                        "Run dash_converter.py to convert HTML files",
                        style={
                            "color": COLORS["text_dim"],
                            "fontSize": "0.75rem",
                        }
                    ),
                ],
                style={"padding": "40px 20px", "textAlign": "center"}
            )
        )

    layout = html.Div(
        [
            # Hidden store for selected visualization
            dcc.Store(id="selected-viz", data=None),

            # Main container
            html.Div(
                [
                    # Sidebar / Gallery panel
                    html.Div(
                        [
                            # Header
                            html.Div(
                                [
                                    html.H1(
                                        APP_TITLE,
                                        style={
                                            "fontSize": "1.4rem",
                                            "fontWeight": "300",
                                            "color": COLORS["accent"],
                                            "margin": "0",
                                            "letterSpacing": "0.05em",
                                        }
                                    ),
                                    html.Div(
                                        APP_SUBTITLE,
                                        style={
                                            "fontSize": "0.7rem",
                                            "color": COLORS["text_secondary"],
                                            "marginTop": "4px",
                                            "letterSpacing": "0.03em",
                                        }
                                    ),
                                    html.Div(
                                        f"{total} visualization{'s' if total != 1 else ''}",
                                        style={
                                            "fontSize": "0.65rem",
                                            "color": COLORS["text_dim"],
                                            "marginTop": "8px",
                                        }
                                    ),
                                ],
                                style={
                                    "padding": "24px 20px 16px 20px",
                                    "borderBottom": f"1px solid {COLORS['border']}",
                                }
                            ),

                            # Gallery list (scrollable)
                            html.Div(
                                gallery_items,
                                style={
                                    "padding": "8px 16px 20px 16px",
                                    "overflowY": "auto",
                                    "flex": "1",
                                }
                            ),

                            # Footer
                            html.Div(
                                [
                                    html.A(
                                        "Tony Quintanilla",
                                        href="https://sites.google.com/view/tony-quintanilla/",
                                        target="_blank",
                                        style={
                                            "color": COLORS["text_dim"],
                                            "textDecoration": "none",
                                            "fontSize": "0.65rem",
                                        }
                                    ),
                                    html.Span(" | ", style={
                                        "color": COLORS["text_dim"],
                                        "fontSize": "0.65rem",
                                    }),
                                    html.A(
                                        "@palomas_orrery",
                                        href="https://www.instagram.com/palomas_orrery/",
                                        target="_blank",
                                        style={
                                            "color": COLORS["text_dim"],
                                            "textDecoration": "none",
                                            "fontSize": "0.65rem",
                                        }
                                    ),
                                ],
                                style={
                                    "padding": "12px 20px",
                                    "borderTop": f"1px solid {COLORS['border']}",
                                    "textAlign": "center",
                                }
                            ),
                        ],
                        style={
                            "width": "280px",
                            "minWidth": "280px",
                            "backgroundColor": COLORS["bg_secondary"],
                            "display": "flex",
                            "flexDirection": "column",
                            "height": "100vh",
                            "borderRight": f"1px solid {COLORS['border']}",
                        }
                    ),

                    # Main content area - visualization
                    html.Div(
                        [
                            # Viz title bar
                            html.Div(
                                [
                                    html.Div(
                                        id="viz-title",
                                        children="Welcome",
                                        style={
                                            "fontSize": "1.1rem",
                                            "fontWeight": "400",
                                            "color": COLORS["text_primary"],
                                            "letterSpacing": "0.02em",
                                        }
                                    ),
                                    html.Div(
                                        id="viz-description",
                                        children="Choose a visualization from the sidebar to explore",
                                        style={
                                            "fontSize": "0.75rem",
                                            "color": COLORS["text_secondary"],
                                            "marginTop": "4px",
                                        }
                                    ),
                                ],
                                style={
                                    "padding": "16px 24px",
                                    "borderBottom": f"1px solid {COLORS['border']}",
                                }
                            ),

                            # Graph container
                            html.Div(
                                dcc.Graph(
                                    id="main-graph",
                                    figure=get_welcome_figure(),
                                    style={"height": "100%", "width": "100%"},
                                    config={
                                        "displayModeBar": True,
                                        "displaylogo": False,
                                        "modeBarButtonsToRemove": [
                                            "lasso2d", "select2d"
                                        ],
                                    },
                                ),
                                style={
                                    "flex": "1",
                                    "padding": "8px",
                                    "overflow": "hidden",
                                }
                            ),
                        ],
                        style={
                            "flex": "1",
                            "display": "flex",
                            "flexDirection": "column",
                            "height": "100vh",
                            "overflow": "hidden",
                            "backgroundColor": COLORS["bg_primary"],
                        }
                    ),
                ],
                style={
                    "display": "flex",
                    "height": "100vh",
                    "overflow": "hidden",
                    "fontFamily": "'Segoe UI', 'Helvetica Neue', sans-serif",
                }
            ),
        ]
    )

    return layout


# ============================================================================
# APP CREATION AND CALLBACKS
# ============================================================================

def create_app(data_folder):
    """Create and configure the Dash application."""

    metadata = load_metadata(data_folder)
    visualizations = metadata.get("visualizations", [])

    # Build lookup dict
    viz_lookup = {v["id"]: v for v in visualizations}

    app = Dash(
        __name__,
        title=APP_TITLE,
        update_title=None,
    )

    app.layout = create_layout(metadata)

    # Custom CSS injected via index_string
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body {
                    background: ''' + COLORS["bg_primary"] + ''';
                    color: ''' + COLORS["text_primary"] + ''';
                    overflow: hidden;
                }
                /* Scrollbar styling */
                ::-webkit-scrollbar { width: 6px; }
                ::-webkit-scrollbar-track { background: transparent; }
                ::-webkit-scrollbar-thumb {
                    background: ''' + COLORS["border"] + ''';
                    border-radius: 3px;
                }
                ::-webkit-scrollbar-thumb:hover {
                    background: ''' + COLORS["text_dim"] + ''';
                }
                /* Card hover effects */
                [id*="viz-card"]:hover {
                    background-color: ''' + COLORS["bg_tertiary"] + ''' !important;
                    border-color: ''' + COLORS["accent_dim"] + ''' !important;
                }
                /* Plotly modebar styling */
                .modebar { background: transparent !important; }
                .modebar-btn path { fill: ''' + COLORS["text_dim"] + ''' !important; }
                .modebar-btn:hover path { fill: ''' + COLORS["accent"] + ''' !important; }
                /* Remove Plotly watermark */
                .js-plotly-plot .plotly .modebar-group:last-child { display: none; }
                /* Mobile responsive */
                @media (max-width: 768px) {
                    body { overflow: auto; }
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''

    # Use pattern-matching callbacks for the card clicks
    from dash import ALL, ctx

    @app.callback(
        Output("main-graph", "figure"),
        Output("viz-title", "children"),
        Output("viz-description", "children"),
        Input({"type": "viz-card", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def update_visualization(n_clicks_list):
        """Load and display the selected visualization."""
        if not ctx.triggered_id:
            return get_welcome_figure(), "Welcome", ""

        viz_id = ctx.triggered_id["index"]
        viz_info = viz_lookup.get(viz_id)

        if not viz_info:
            return get_welcome_figure(), "Not Found", "Visualization not found"

        filename = viz_info.get("filename", "")
        fig = load_figure(data_folder, filename)

        if fig is None:
            return (
                get_welcome_figure(),
                viz_info.get("title", "Error"),
                f"Could not load {filename}"
            )

        title = viz_info.get("title", "Untitled")
        desc = viz_info.get("description", "")
        cat_label = viz_info.get("category_label", "")
        if cat_label and desc:
            subtitle = f"{cat_label} - {desc}"
        elif cat_label:
            subtitle = cat_label
        else:
            subtitle = desc

        return fig, title, subtitle

    return app


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Paloma's Orrery - Dash Gallery")
    parser.add_argument("--folder", default=DEFAULT_DATA_FOLDER,
                       help="Data folder containing JSON files and metadata")
    parser.add_argument("--port", type=int, default=8050,
                       help="Port to run the server on")
    parser.add_argument("--debug", action="store_true",
                       help="Run in debug mode (auto-reload on changes)")
    parser.add_argument("--host", default="127.0.0.1",
                       help="Host to bind to (use 0.0.0.0 for network access)")

    args = parser.parse_args()

    # Resolve data folder
    data_folder = os.path.abspath(args.folder)
    if not os.path.isdir(data_folder):
        print(f"Data folder not found: {data_folder}")
        print(f"Run dash_converter.py first to create visualization data.")
        sys.exit(1)

    metadata_path = os.path.join(data_folder, METADATA_FILE)
    if not os.path.exists(metadata_path):
        print(f"No {METADATA_FILE} found in {data_folder}")
        print(f"Run dash_converter.py first to convert HTML files.")
        sys.exit(1)

    metadata = load_metadata(data_folder)
    count = metadata.get("total_count", 0)

    print(f"{'=' * 50}")
    print(f"  Paloma's Orrery - Dash Gallery")
    print(f"  Data folder: {data_folder}")
    print(f"  Visualizations: {count}")
    print(f"  URL: http://{args.host}:{args.port}/")
    print(f"{'=' * 50}")

    app = create_app(data_folder)
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
