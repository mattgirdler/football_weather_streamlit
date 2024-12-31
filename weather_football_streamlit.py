import pandas as pd
import streamlit as st
import plotly.express as px

st.title("Weather vs Football - Data Analysis")
st.text("""
        This Streamlit app aims to demonstrate the correlation (if any) between adverse weather conditions and football style/results.

        It includes the Statsbomb match metric data from all matches in the 23/24 football season in the Premier League, Championship, League One and League Two. This data is combined with Met Office Pseudo-Observation data for the relevant stadium postcodes and kick-off times for each match.
        """)

tab1, tab2, tab3, tab4 = st.tabs(["Season Scatter Chart", "Per-Match Scatter Chart", "Correlation Bar Chart", "Raw Data"])

multiteam_data = pd.read_csv('../statsbomb-data-analysis/data/weather_impact_summary_multiteam.csv')
combined_data = pd.read_csv('../statsbomb-data-analysis/data/combined_match_stats_with_weather.csv')

with st.sidebar:
    weather_metric = st.selectbox(
        "Select weather metric",
        multiteam_data["weather_metric"].unique(),
        index=0)
    match_metric = st.selectbox(
        "Select match metric",
        multiteam_data["match_metric"].unique(),
        index=0)
    match_metric_caption = match_metric.replace("_", " ").title()
    weather_metric_caption = weather_metric.replace("_", " ").title()
with tab1:
    filtered_metrics = multiteam_data[
        (multiteam_data['match_metric'] == match_metric) &
        (multiteam_data['weather_metric'] == weather_metric)
    ].sort_values("team_name")
    fig = px.scatter(
        filtered_metrics,
        x="team_average_weather_metric",
        y="team_average_match_metric",
        color="team_name",
        trendline="ols")
    fig.update_layout(dict(title=f"23/24 Season<br><sup>{match_metric_caption} vs {weather_metric_caption}</sup>"))
    st.plotly_chart(fig, theme="streamlit")

with tab2:
    selected_team = st.selectbox("Select team", sorted(combined_data["team_name"].unique()), index=0)
    filtered_team_data = combined_data[combined_data["team_name"] == selected_team]
    filtered_team_data["Home/Away"] = filtered_team_data["home_team"].apply(
        lambda x: "Home" if x == selected_team else "Away"
    )
    display_home_away = st.checkbox("Display Home/Away", value=True)
    color_column = "Home/Away" if display_home_away else "team_name"
    if display_home_away:
        fig = px.scatter(
            filtered_team_data,
            x=weather_metric,
            y=match_metric,
            color=color_column,
            trendline="ols",
            hover_data=["opposition_name", "competition_name", "match_date", "kick_off"],
        )
    else:
        fig = px.scatter(
            filtered_team_data,
            x=weather_metric,
            y=match_metric,
            trendline="ols",
            hover_data=["opposition_name", "competition_name", "match_date", "kick_off"],
            hover_name="match_date"
        )
    fig.update_layout(dict(title=f"{selected_team} 23/24 Season<br><sup>{match_metric_caption} vs {weather_metric_caption}</sup>"))
    st.plotly_chart(fig, theme="streamlit")

with tab3:
    fig = px.bar(filtered_metrics,
                x="team_name",
                y="correlation")
    fig.update_layout(dict(title=f"23/24 Season<br><sup>{match_metric_caption} vs {weather_metric_caption}</sup>"))
    st.plotly_chart(fig, theme="streamlit")
with tab4:
    st.dataframe(combined_data)


st.text("""
Weather data: © Crown copyright 2024, Met Office
Match data: Copyright © 2024 Hudl Statsbomb
""")