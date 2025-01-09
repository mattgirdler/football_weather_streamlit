import hmac
import pandas as pd
import streamlit as st
import plotly.express as px


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.


st.title("Weather vs Football - Data Analysis")
st.text("""
        This Streamlit app aims to demonstrate the correlation (if any) between adverse weather conditions and football style/results.

        It includes the Statsbomb match metric data from all matches in the 23/24 football season in the Premier League, Championship, League One and League Two. This data is combined with Met Office Best Estimate Observation data for the relevant stadium postcodes and kick-off times for each match.
        """)

tab1, tab2, tab3, tab4 = st.tabs(["Season Scatter Chart", "Per-Match Scatter Chart", "Correlation Bar Chart", "Raw Data"])

# long_data = pd.read_csv('data/weather_impact_summary_long.csv')
combined_data = pd.read_csv('data/combined_match_stats_with_weather.csv')

weather_values = ["total_rainfall_amount_previous_hour", "wind_speed_10m", "wind_gust_10m", "feels_like_temperature"]
match_metrics = ["team_match_directness", "team_match_pace_towards_goal", "team_match_gk_pass_distance",
                 "team_match_gk_long_pass_ratio", "team_match_ball_in_play_time", "team_match_dribble_ratio",
                 "team_match_high_press_shots_conceded", "team_match_passing_ratio"]

with st.sidebar:
    selected_weather_metric = st.selectbox(
        "Select weather metric",
        weather_values,
        index=0)
    selected_match_metric = st.selectbox(
        "Select match metric",
        match_metrics,
        index=0)
    match_metric_caption = selected_match_metric.replace("_", " ").title()
    weather_metric_caption = selected_weather_metric.replace("_", " ").title()
    should_apply_weather_metric_upper_limit = st.checkbox("Apply weather metric upper limit") 
    weather_metric_upper_limit = st.number_input(
        "Upper limit value",
        disabled=bool(not should_apply_weather_metric_upper_limit),
        min_value=0,
        value=10
    )

print(selected_weather_metric)
print(selected_match_metric) 

# Apply an upper limit to a particular weather column to avoid outliers skewing the data
if should_apply_weather_metric_upper_limit:
    combined_data[selected_weather_metric] = combined_data[selected_weather_metric].clip(upper=weather_metric_upper_limit)

# Create correlation dataframe
results = []

average_weather_metric = combined_data[selected_weather_metric].mean()
average_match_metric = combined_data[selected_weather_metric].mean()

for team_name in combined_data['team_name'].unique():
    team_stats = combined_data[combined_data['team_name'] == team_name]

    # Precompute team-specific averages for the specified weather and all match metrics
    team_average_weather_metric = team_stats[selected_weather_metric].mean()
    team_average_match_metrics = team_stats[selected_match_metric].mean()

    results.append({
        "team_name": team_name,
        "weather_metric": selected_weather_metric,
        "match_metric": selected_match_metric,
        "average_weather_metric": average_weather_metric,
        "average_match_metric": average_match_metric,
        "team_average_match_metric": team_average_match_metrics,
        "team_average_weather_metric": team_average_weather_metric,
        "correlation": team_stats[selected_weather_metric].corr(team_stats[selected_match_metric])
    })

long_data = pd.DataFrame(results)

filtered_metrics = long_data[
    (long_data['match_metric'] == selected_match_metric) &
    (long_data['weather_metric'] == selected_weather_metric)
].sort_values("team_name")

pearson = round(combined_data[selected_weather_metric].corr(combined_data[selected_match_metric]), 4)
print(pearson)

with tab1:
    display_team_name = st.checkbox("Display Team Name")
    if display_team_name:
        fig = px.scatter(
            filtered_metrics,
            x="team_average_weather_metric",
            y="team_average_match_metric",
            hover_data=["team_name", "weather_metric", "match_metric", "average_weather_metric", "average_match_metric"],
            color="team_name")
    else:
        fig = px.scatter(
            filtered_metrics,
            x="team_average_weather_metric",
            y="team_average_match_metric",
            hover_data=["team_name", "weather_metric", "match_metric", "average_weather_metric", "average_match_metric"],
            trendline="ols")
    if should_apply_weather_metric_upper_limit:
        fig.update_layout(dict(title=f"23/24 Season<br><sup>{match_metric_caption} vs {weather_metric_caption} (upper limit = {weather_metric_upper_limit}) </sup>"))
    else:
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
            x=selected_weather_metric,
            y=selected_match_metric,
            color=color_column,
            trendline="ols",
            hover_data=["match_id", "team_name", "opposition_name", "competition_name", "match_date", "kick_off"],
        )
    else:
        fig = px.scatter(
            filtered_team_data,
            x=selected_weather_metric,
            y=selected_match_metric,
            trendline="ols",
            hover_data=["match_id", "team_name", "opposition_name", "competition_name", "match_date", "kick_off"],
            hover_name="match_date"
        )
    if should_apply_weather_metric_upper_limit:
        fig.update_layout(dict(title=f"{selected_team} 23/24 Season<br><sup>{match_metric_caption} vs {weather_metric_caption} (upper limit = {weather_metric_upper_limit}) </sup>"))
    else:
        fig.update_layout(dict(title=f"{selected_team} 23/24 Season<br><sup>{match_metric_caption} vs {weather_metric_caption}</sup>"))
    st.plotly_chart(fig, theme="streamlit")

with tab3:
    sort_by_team_name = st.checkbox("Sort by team name", value=True)
    if sort_by_team_name:
        filtered_metrics = filtered_metrics.sort_values("team_name")
    else:
        filtered_metrics = filtered_metrics.sort_values("correlation")
    fig = px.bar(filtered_metrics,
            x="team_name",
            y="correlation")
    fig.add_hline(
        pearson, line_width=2, line_dash="dash", line_color="white",
        annotation_text=f"<b>Pearson Value: {pearson}</b>", annotation_position="bottom right",
        annotation_font_size=14, annotation_font_color="white"
    )
    if should_apply_weather_metric_upper_limit:
        fig.update_layout(dict(
            title=f"23/24 Season<br><sup>{match_metric_caption} vs {weather_metric_caption} (upper limit = {weather_metric_upper_limit}) </sup>"
            ))
    else:
        fig.update_layout(dict(
            title=f"23/24 Season<br><sup>{match_metric_caption} vs {weather_metric_caption}</sup>"
            ))
    st.plotly_chart(fig, theme="streamlit")
with tab4:
    st.write("Full match metrics and weather observations")
    st.dataframe(combined_data)
    st.write("Team metrics/correlations")
    st.dataframe(filtered_metrics)


st.text("""
Weather data: © Crown copyright 2024, Met Office
Match data: Copyright © 2024 Hudl Statsbomb
""")
