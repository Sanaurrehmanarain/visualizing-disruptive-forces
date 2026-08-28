from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import plotly.graph_objects as go
from pathlib import Path
from io import BytesIO

# ==========================================
# 1. LOAD DATA SECURELY
# ==========================================
possible_paths = [
    Path("data/processed/bis_cbs_network_2007_2010_positive_edges.csv"),
    Path("../data/processed/bis_cbs_network_2007_2010_positive_edges.csv"),
]

df_global = pd.DataFrame()
data_load_error = None
for p in possible_paths:
    if p.exists():
        try:
            df_global = pd.read_csv(p)
        except Exception as e:
            data_load_error = f"Found file at {p} but failed to read it: {e}"
        break
else:
    data_load_error = (
        "Could not find 'bis_cbs_network_2007_2010_positive_edges.csv' in "
        "data/processed/ or ../data/processed/. All panels will be empty until "
        "the file is available."
    )

REQUIRED_COLS = {"period", "Reporting country", "Counterparty country", "claim_value_usd_millions"}
if not df_global.empty and not REQUIRED_COLS.issubset(df_global.columns):
    missing = REQUIRED_COLS - set(df_global.columns)
    data_load_error = f"Data file is missing expected column(s): {', '.join(sorted(missing))}"
    df_global = pd.DataFrame()

available_quarters = sorted(df_global["period"].unique().tolist()) if not df_global.empty else []
default_first_q = available_quarters[0] if available_quarters else "2008-Q1"
default_last_q = available_quarters[-1] if available_quarters else "2008-Q1"

all_countries = (
    sorted(set(df_global["Reporting country"].unique()) | set(df_global["Counterparty country"].unique()))
    if not df_global.empty
    else []
)
default_target = "United States" if "United States" in all_countries else (all_countries[0] if all_countries else "N/A")

# Fallback choices so dropdowns are never empty even without data
_quarter_choices = available_quarters if available_quarters else ["2008-Q1"]
_country_choices = all_countries if all_countries else ["N/A"]

# ==========================================
# 2. HELPERS
# ==========================================
def style_ax(ax, title, ylabel, xlabel, rotation=25):
    """Shared matplotlib styling so every chart looks consistent."""
    ax.set_title(title, fontweight="bold", fontsize=16, pad=20)
    ax.set_ylabel(ylabel, fontweight="bold", labelpad=15)
    ax.set_xlabel(xlabel, fontweight="bold", labelpad=15)
    plt.setp(ax.get_xticklabels(), rotation=rotation, ha="right", fontsize=11)
    plt.setp(ax.get_yticklabels(), fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.6)


def empty_fig(message="No data available for this selection."):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=14, color="gray")
    ax.axis("off")
    return fig


def hhi(shares_series):
    """Herfindahl-Hirschman Index on a 0-10000 scale from raw exposure values."""
    total = shares_series.sum()
    if total <= 0:
        return 0.0
    shares = shares_series / total
    return float((shares ** 2).sum() * 10000)


def network_density(df):
    """Directed-edge density: actual bilateral ties / all possible directed pairs."""
    if df.empty:
        return 0.0
    nodes = set(df["Reporting country"]) | set(df["Counterparty country"])
    n = len(nodes)
    if n < 2:
        return 0.0
    possible = n * (n - 1)
    actual = len(df[["Reporting country", "Counterparty country"]].drop_duplicates())
    return actual / possible


# ==========================================
# 3. UI DEFINITION
# ==========================================
app_ui = ui.page_navbar(
    # --- POSITIONAL ARGUMENTS FIRST (THE TABS) ---
    # TAB 1: Structural Network
    ui.nav_panel(
        "1. Network Cartography",
        ui.layout_sidebar(
            ui.sidebar(
                ui.h4("Topology Controls"),
                ui.input_select(id="q_net", label="Select Quarter", choices=_quarter_choices, selected=default_first_q),
                ui.input_slider(id="top_n", label="Top Hubs to Display", min=3, max=15, value=5),
                ui.hr(),
                ui.p(
                    "Identify the structural core of the network and track exposure in real-time.",
                    style="font-size: 0.9em; color: gray;",
                ),
            ),
            ui.layout_columns(
                ui.value_box("Total Global Exposure", ui.output_text("kpi_exposure"), theme="bg-blue"),
                ui.value_box("Active Cross-Border Ties", ui.output_text("kpi_edges"), theme="bg-green"),
                ui.value_box("Average Claim Size", ui.output_text("kpi_avg"), theme="bg-purple"),
            ),
            ui.layout_columns(
                ui.value_box("Lender Concentration (HHI)", ui.output_text("kpi_hhi"), theme="bg-orange"),
                ui.value_box("Network Density", ui.output_text("kpi_density"), theme="bg-indigo"),
                ui.value_box("Exposure QoQ Change", ui.output_text("kpi_qoq"), theme="bg-red"),
                ui.value_box("Largest Single Bilateral Tie", ui.output_text("kpi_max_edge"), theme="bg-gray"),
            ),
            ui.card(
                ui.card_header("Top Lenders — Bar View"),
                ui.output_plot("hub_plot", height="500px"),
            ),
            ui.card(
                ui.card_header("Global Exposure Network — Interactive Graph"),
                ui.p(
                    "Node size = total exposure. Edge width/darkness = bilateral claim size. Drag, zoom and hover for details.",
                    style="font-size: 0.85em; color: gray;",
                ),
                output_widget("network_graph"),
            ),
        ),
    ),
    # TAB 2: Causal Dynamics
    ui.nav_panel(
        "2. Causal Dynamics",
        ui.layout_sidebar(
            ui.sidebar(
                ui.h4("Timeline Controls"),
                ui.input_radio_buttons(
                    "timeline_metric",
                    "Select Metric to Track",
                    choices=["Total Claims (USD)", "Number of Active Ties"],
                    selected="Total Claims (USD)",
                ),
                ui.input_slider(
                    id="q_range",
                    label="Quarter Range",
                    min=0,
                    max=max(len(_quarter_choices) - 1, 0),
                    value=(0, max(len(_quarter_choices) - 1, 0)),
                    step=1,
                ),
                ui.output_text("q_range_label"),
                ui.hr(),
                ui.download_button("download_timeline", "Download filtered data (CSV)"),
                ui.p(
                    "Observe the nonlinear phase transitions and cliff-edge crashes over time.",
                    style="font-size: 0.9em; color: gray; margin-top: 10px;",
                ),
            ),
            ui.card(
                ui.output_plot("timeline_plot", height="550px"),
            ),
        ),
    ),
    # TAB 3: Strategic Behavior
    ui.nav_panel(
        "3. Strategic Behavior",
        ui.layout_sidebar(
            ui.sidebar(
                ui.h4("Bank Run Controls"),
                ui.input_select("target_country", "Common Exposure (Target)", choices=_country_choices, selected=default_target),
                ui.input_select("pre_q", "Pre-Crash Quarter", choices=_quarter_choices, selected=default_first_q),
                ui.input_select("post_q", "Post-Crash Quarter", choices=_quarter_choices, selected=default_last_q),
                ui.input_slider(id="n_lenders", label="Number of Lenders to Compare", min=3, max=10, value=5),
                ui.p("Compare specific quarters to observe simultaneous strategic capital flight."),
            ),
            ui.card(
                ui.output_plot("flight_plot", height="550px"),
            ),
        ),
    ),
    # --- KEYWORD ARGUMENTS LAST (TITLE & ID) ---
    title="Visualizing Disruptive Forces",
    id="main_nav",
    header=ui.output_ui("data_warning"),
)


# ==========================================
# 4. SERVER LOGIC
# ==========================================
def server(input, output, session):

    @reactive.Calc
    def get_data():
        return df_global

    @output
    @render.ui
    def data_warning():
        if data_load_error:
            return ui.div(
                ui.markdown(f"**⚠️ Data issue:** {data_load_error}"),
                style=(
                    "background-color:#fff3cd; color:#664d03; padding:10px 16px; "
                    "border-bottom:1px solid #ffe69c; font-size:0.9em;"
                ),
            )
        return None

    # ------------------------------------------
    # TAB 1: KPIs, HUB PLOT & NETWORK GRAPH
    # ------------------------------------------
    @reactive.Calc
    def current_quarter_data():
        df = get_data()
        if df.empty:
            return pd.DataFrame()
        return df[df["period"] == input.q_net()]

    @reactive.Calc
    def previous_quarter_data():
        df = get_data()
        if df.empty or not available_quarters or input.q_net() not in available_quarters:
            return pd.DataFrame()
        idx = available_quarters.index(input.q_net())
        if idx == 0:
            return pd.DataFrame()
        return df[df["period"] == available_quarters[idx - 1]]

    @output
    @render.text
    def kpi_exposure():
        q_data = current_quarter_data()
        if q_data.empty:
            return "$0"
        total = q_data["claim_value_usd_millions"].sum()
        return f"${total / 1e6:,.2f} Trillion"

    @output
    @render.text
    def kpi_edges():
        q_data = current_quarter_data()
        if q_data.empty:
            return "0"
        return f"{len(q_data):,} edges"

    @output
    @render.text
    def kpi_avg():
        q_data = current_quarter_data()
        if q_data.empty:
            return "$0"
        avg = q_data["claim_value_usd_millions"].mean()
        return f"${avg:,.0f} Million"

    @output
    @render.text
    def kpi_hhi():
        q_data = current_quarter_data()
        if q_data.empty:
            return "N/A"
        lenders = q_data.groupby("Reporting country")["claim_value_usd_millions"].sum()
        score = hhi(lenders)
        label = "Concentrated" if score > 2500 else ("Moderate" if score > 1500 else "Diverse")
        return f"{score:,.0f} ({label})"

    @output
    @render.text
    def kpi_density():
        q_data = current_quarter_data()
        if q_data.empty:
            return "N/A"
        return f"{network_density(q_data) * 100:.1f}%"

    @output
    @render.text
    def kpi_qoq():
        q_data = current_quarter_data()
        p_data = previous_quarter_data()
        if q_data.empty or p_data.empty:
            return "N/A"
        curr = q_data["claim_value_usd_millions"].sum()
        prev = p_data["claim_value_usd_millions"].sum()
        if prev == 0:
            return "N/A"
        pct = (curr - prev) / prev * 100
        arrow = "▲" if pct >= 0 else "▼"
        return f"{arrow} {pct:+.1f}%"

    @output
    @render.text
    def kpi_max_edge():
        q_data = current_quarter_data()
        if q_data.empty:
            return "N/A"
        row = q_data.loc[q_data["claim_value_usd_millions"].idxmax()]
        return f"{row['Reporting country']} → {row['Counterparty country']} (${row['claim_value_usd_millions']/1e3:,.1f}B)"

    @output
    @render.plot
    def hub_plot():
        q_data = current_quarter_data()
        if q_data.empty:
            return empty_fig()

        lenders = q_data.groupby("Reporting country")["claim_value_usd_millions"].sum().reset_index()
        lenders = lenders.sort_values("claim_value_usd_millions", ascending=False).head(input.top_n())

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(
            data=lenders,
            x="Reporting country",
            y="claim_value_usd_millions",
            hue="Reporting country",
            ax=ax,
            palette="Reds_r",
            legend=False,
        )
        style_ax(
            ax,
            f"Top {input.top_n()} Global Lenders in {input.q_net()}",
            "Total Outward Exposure (USD Millions)",
            "Reporting Country",
        )
        fig.tight_layout()
        return fig

    @output
    @render_widget
    def network_graph():
        q_data = current_quarter_data()
        if q_data.empty:
            fig = go.Figure()
            fig.update_layout(
                annotations=[dict(text="No data available for this quarter.", showarrow=False, font=dict(size=16))],
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                height=550,
            )
            return fig

        top_n = input.top_n()
        # Keep the graph readable: top lenders plus everyone they lend to
        top_lenders = (
            q_data.groupby("Reporting country")["claim_value_usd_millions"]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
            .index
        )
        sub = q_data[q_data["Reporting country"].isin(top_lenders)]

        G = nx.DiGraph()
        for _, r in sub.iterrows():
            G.add_edge(
                r["Reporting country"],
                r["Counterparty country"],
                weight=r["claim_value_usd_millions"],
            )

        if G.number_of_nodes() == 0:
            fig = go.Figure()
            fig.update_layout(height=550)
            return fig

        pos = nx.spring_layout(G, k=0.9, seed=42, weight="weight")

        exposure_by_node = sub.groupby("Reporting country")["claim_value_usd_millions"].sum()
        max_exposure = exposure_by_node.max() if not exposure_by_node.empty else 1
        max_weight = max((d["weight"] for _, _, d in G.edges(data=True)), default=1)

        edge_traces = []
        for u, v, d in G.edges(data=True):
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            width = 1 + 6 * (d["weight"] / max_weight)
            edge_traces.append(
                go.Scatter(
                    x=[x0, x1],
                    y=[y0, y1],
                    mode="lines",
                    line=dict(width=width, color="rgba(192,57,43,0.35)"),
                    hoverinfo="text",
                    text=f"{u} → {v}<br>${d['weight']:,.0f}M",
                    showlegend=False,
                )
            )

        node_x, node_y, node_size, node_text, node_color = [], [], [], [], []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            exp = exposure_by_node.get(node, 1)
            node_size.append(15 + 45 * (exp / max_exposure) if node in top_lenders else 14)
            node_color.append("#c0392b" if node in top_lenders else "#2c3e50")
            node_text.append(f"{node}<br>Exposure: ${exp:,.0f}M" if node in exposure_by_node.index else node)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=list(G.nodes()),
            textposition="top center",
            hoverinfo="text",
            hovertext=node_text,
            marker=dict(size=node_size, color=node_color, line=dict(width=1, color="white")),
            showlegend=False,
        )

        fig = go.Figure(data=edge_traces + [node_trace])
        fig.update_layout(
            title=f"Cross-Border Exposure Network — {input.q_net()}",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            height=550,
            plot_bgcolor="white",
            margin=dict(l=10, r=10, t=50, b=10),
        )
        return fig

    # ------------------------------------------
    # TAB 2: TIMELINE PLOT
    # ------------------------------------------
    @reactive.Calc
    def selected_quarter_range():
        lo, hi = input.q_range()
        lo, hi = int(lo), int(hi)
        if not available_quarters:
            return []
        lo = max(0, min(lo, len(available_quarters) - 1))
        hi = max(0, min(hi, len(available_quarters) - 1))
        if lo > hi:
            lo, hi = hi, lo
        return available_quarters[lo : hi + 1]

    @output
    @render.text
    def q_range_label():
        qs = selected_quarter_range()
        if not qs:
            return "No quarters selected"
        return f"Showing: {qs[0]} → {qs[-1]} ({len(qs)} quarters)"

    @reactive.Calc
    def timeline_filtered():
        df = get_data()
        qs = selected_quarter_range()
        if df.empty or not qs:
            return pd.DataFrame()
        return df[df["period"].isin(qs)]

    @output
    @render.plot
    def timeline_plot():
        df = timeline_filtered()
        if df.empty:
            return empty_fig()

        fig, ax = plt.subplots(figsize=(10, 6))

        if input.timeline_metric() == "Total Claims (USD)":
            timeline = df.groupby("period")["claim_value_usd_millions"].sum().reset_index()
            ax.plot(
                timeline["period"],
                timeline["claim_value_usd_millions"] / 1e6,
                marker="o",
                color="#c0392b",
                linewidth=3,
                markersize=8,
            )
            style_ax(ax, "Nonlinear Systemic Shock: Total Global Claims", "Total Claims (Trillions USD)", "Quarter", rotation=45)
        else:
            timeline = df.groupby("period").size().reset_index(name="active_ties")
            ax.plot(
                timeline["period"],
                timeline["active_ties"],
                marker="s",
                color="#2980b9",
                linewidth=3,
                markersize=8,
            )
            style_ax(ax, "Network Density: Active Cross-Border Connections", "Number of Active Ties", "Quarter", rotation=45)

        fig.tight_layout()
        return fig

    @render.download(filename="filtered_network_timeline.csv")
    def download_timeline():
        df = timeline_filtered()
        buf = BytesIO()
        df.to_csv(buf, index=False)
        buf.seek(0)
        yield buf.read()

    # ------------------------------------------
    # TAB 3: BANK RUN PLOT
    # ------------------------------------------
    @output
    @render.plot
    def flight_plot():
        df = get_data()
        if df.empty:
            return empty_fig()

        target = input.target_country()
        borrowing = df[df["Counterparty country"] == target]

        # Dynamically derive the biggest lenders to this target (excluding the target itself)
        key_lenders = (
            borrowing[borrowing["Reporting country"] != target]
            .groupby("Reporting country")["claim_value_usd_millions"]
            .sum()
            .sort_values(ascending=False)
            .head(input.n_lenders())
            .index
        )
        borrowing_key = borrowing[borrowing["Reporting country"].isin(key_lenders)]

        df_pre = borrowing_key[borrowing_key["period"] == input.pre_q()][["Reporting country", "claim_value_usd_millions"]]
        df_pre = df_pre.rename(columns={"claim_value_usd_millions": f"{input.pre_q()} (Pre)"})

        df_post = borrowing_key[borrowing_key["period"] == input.post_q()][["Reporting country", "claim_value_usd_millions"]]
        df_post = df_post.rename(columns={"claim_value_usd_millions": f"{input.post_q()} (Post)"})

        merged = pd.merge(df_pre, df_post, on="Reporting country", how="outer").fillna(0)
        if merged.empty:
            return empty_fig("No overlapping data for selected quarters.")

        merged["Drop"] = merged[f"{input.pre_q()} (Pre)"] - merged[f"{input.post_q()} (Post)"]
        merged = merged.sort_values("Drop", ascending=False)

        melted = merged.melt(
            id_vars="Reporting country",
            value_vars=[f"{input.pre_q()} (Pre)", f"{input.post_q()} (Post)"],
            var_name="Period",
            value_name="Exposure",
        )

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=melted, x="Reporting country", y="Exposure", hue="Period", ax=ax, palette=["#2c3e50", "#e74c3c"])
        style_ax(
            ax,
            f"Strategic Capital Flight from {target}",
            "Exposure (USD Millions)",
            "Reporting Country (Lender)",
            rotation=15,
        )
        ax.legend(title="Quarter", fontsize=11, title_fontsize=12)
        fig.tight_layout()
        return fig


app = App(app_ui, server)
