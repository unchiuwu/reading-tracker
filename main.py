# READING ANALYTICS DASHBOARD

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from data_processing import get_data


# PAGE CONFIGURATION

st.set_page_config(
    page_title="Reading Analytics",
    page_icon="📚",
    layout="wide"
)


# CUSTOM CSS

st.markdown(
    """
    <style>

    .main {
        background-color: #f8f9fa;
    }

    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# LOAD DATA

@st.cache_data(ttl=300)
def load_processed_data():

    return get_data()


df = load_processed_data()

# SIDEBAR

st.sidebar.title("Reading Analytics")

st.sidebar.markdown(
    """
    **Interactive Reading Data Dashboard**

    Explore reading activity, language patterns,
    temporal trends and completion behaviour.
    """
)

st.sidebar.divider()


# FILTERS

status_options = sorted(
    df["Status"]
    .dropna()
    .unique()
    .tolist()
)

language_options = sorted(
    df["Language"]
    .dropna()
    .unique()
    .tolist()
)

selected_status = st.sidebar.multiselect(
    "Reading Status",
    options=status_options,
    default=status_options
)

selected_languages = st.sidebar.multiselect(
    "Language",
    options=language_options,
    default=language_options
)


filtered_df = df[
    df["Status"].isin(selected_status)
    & df["Language"].isin(selected_languages)
].copy()


# HEADER

st.title("📚 Reading Analytics Dashboard")

st.markdown(
    """
    An interactive exploration of reading behaviour, book metadata,
    language distribution and temporal reading patterns.
    """
)

st.divider()


# KPI SECTION

total_books = len(filtered_df)

total_read = filtered_df["Status"].eq("Read").sum()

total_tbr = filtered_df["Status"].eq("To Be Read").sum()

unknown_year = (
    filtered_df["Status"].eq("Read")
    & filtered_df["Finish_Year"].isna()
).sum()

known_year = (
    filtered_df["Status"].eq("Read")
    & filtered_df["Finish_Year"].notna()
).sum()


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Books",
    f"{total_books:,}"
)

col2.metric(
    "Books Read",
    f"{total_read:,}"
)

col3.metric(
    "To Be Read",
    f"{total_tbr:,}"
)

col4.metric(
    "Unknown Completion Year",
    f"{unknown_year:,}"
)


st.divider()


# SECTION 1  READING STATUS

st.header("Reading Status")

status_counts = (
    filtered_df["Status"]
    .value_counts()
    .reset_index()
)

status_counts.columns = [
    "Status",
    "Books"
]

fig_status = px.bar(
    status_counts,
    x="Status",
    y="Books",
    color="Status",
    text="Books",
    title="Reading Status Distribution"
)

fig_status.update_layout(
    showlegend=False
)

st.plotly_chart(
    fig_status,
    use_container_width=True
)


# SECTION 2  LANGUAGE

st.header("Language Analysis")

col1, col2 = st.columns(2)


with col1:

    language_counts = (
        filtered_df["Language"]
        .value_counts()
        .reset_index()
    )

    language_counts.columns = [
        "Language",
        "Books"
    ]

    fig_language = px.pie(
        language_counts,
        names="Language",
        values="Books",
        hole=0.4,
        title="Language Distribution"
    )

    st.plotly_chart(
        fig_language,
        use_container_width=True
    )


with col2:

    read_df = filtered_df[
        filtered_df["Status"].eq("Read")
    ]

    read_language = (
        read_df["Language"]
        .value_counts()
        .reset_index()
    )

    read_language.columns = [
        "Language",
        "Books_Read"
    ]

    fig_read_language = px.bar(
        read_language,
        x="Language",
        y="Books_Read",
        color="Language",
        text="Books_Read",
        title="Completed Books by Language"
    )

    fig_read_language.update_layout(
        showlegend=False
    )

    st.plotly_chart(
        fig_read_language,
        use_container_width=True
    )


# SECTION 3  BOOK TYPES

st.header("Book Type Analysis")

type_counts = (
    filtered_df["Type"]
    .value_counts()
    .reset_index()
)

type_counts.columns = [
    "Type",
    "Books"
]

fig_types = px.bar(
    type_counts,
    x="Type",
    y="Books",
    color="Type",
    text="Books",
    title="Book Type Distribution"
)

fig_types.update_layout(
    showlegend=False
)

st.plotly_chart(
    fig_types,
    use_container_width=True
)


# SECTION 4  ANNUAL READING

st.header("Reading Trends Over Time")

read_df = filtered_df[
    filtered_df["Status"].eq("Read")
].copy()


# Known completion years

annual_data = (
    read_df[
        read_df["Reading_Year"] > 0
    ]
    .groupby(
        "Reading_Year"
    )
    .size()
    .reset_index(
        name="Books_Read"
    )
)

annual_data["Reading_Year"] = (
    annual_data["Reading_Year"]
    .astype(int)
)

annual_data = annual_data.sort_values(
    "Reading_Year"
)


fig_annual = px.line(
    annual_data,
    x="Reading_Year",
    y="Books_Read",
    markers=True,
    title="Books Completed by Year"
)

fig_annual.update_layout(
    xaxis_title="Completion Year",
    yaxis_title="Books Read"
)

st.plotly_chart(
    fig_annual,
    use_container_width=True
)


# SECTION 5  YEAR × LANGUAGE

st.subheader("Annual Reading Volume by Language")

annual_language = (
    read_df
    .groupby(
        ["Reading_Year", "Language"]
    )
    .size()
    .reset_index(
        name="Books_Read"
    )
)

annual_language["Year_Label"] = (
    annual_language["Reading_Year"]
    .apply(
        lambda x:
        "????"
        if x == 0
        else str(int(x))
    )
)

annual_language["Sort_Order"] = (
    annual_language["Reading_Year"]
    .replace(0, np.inf)
)

annual_language = (
    annual_language
    .sort_values("Sort_Order")
)


fig_annual_language = px.bar(
    annual_language,
    x="Year_Label",
    y="Books_Read",
    color="Language",
    barmode="group",
    text="Books_Read",
    title="Completed Books by Year and Language"
)

fig_annual_language.update_layout(
    xaxis_title="Completion Year",
    yaxis_title="Books Read"
)

st.plotly_chart(
    fig_annual_language,
    use_container_width=True
)


# SECTION 6  MONTHLY ANALYSIS

st.header("Monthly Reading Patterns")

monthly_read_df = read_df[
    read_df["Finish_Month"].notna()
].copy()


start_month_df = read_df[
    read_df["Start_Month"].notna()
].copy()


month_names = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
]


# Monthly completion counts

completion_counts = (
    monthly_read_df["Finish_Month"]
    .value_counts()
    .reindex(
        range(1, 13),
        fill_value=0
    )
)


# Monthly start counts

start_counts = (
    start_month_df["Start_Month"]
    .value_counts()
    .reindex(
        range(1, 13),
        fill_value=0
    )
)


monthly_comparison = pd.DataFrame({
    "Month": month_names,
    "Books Started": start_counts.values,
    "Books Completed": completion_counts.values
})


monthly_plot = monthly_comparison.melt(
    id_vars="Month",
    var_name="Reading Event",
    value_name="Books"
)


fig_monthly = px.bar(
    monthly_plot,
    x="Month",
    y="Books",
    color="Reading Event",
    barmode="group",
    title="Books Started vs Completed by Month"
)

fig_monthly.update_layout(
    xaxis_tickangle=-45
)

st.plotly_chart(
    fig_monthly,
    use_container_width=True
)


# SECTION 7  START × COMPLETION MONTH

st.subheader(
    "Start Month vs Completion Month"
)

start_finish_df = read_df[
    read_df["Start_Month"].notna()
    & read_df["Finish_Month"].notna()
].copy()


start_finish_matrix = pd.crosstab(
    start_finish_df["Start_Month"],
    start_finish_df["Finish_Month"]
)


start_finish_matrix = (
    start_finish_matrix
    .reindex(
        index=range(1, 13),
        fill_value=0
    )
    .reindex(
        columns=range(1, 13),
        fill_value=0
    )
)


start_finish_matrix.index = month_names
start_finish_matrix.columns = month_names


fig_heatmap = px.imshow(
    start_finish_matrix,
    text_auto=True,
    color_continuous_scale="Blues",
    labels={
        "x": "Completion Month",
        "y": "Start Month",
        "color": "Books"
    },
    title="Book Starts vs Completion Months"
)

st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)


# SECTION 8  PUBLICATION YEAR

st.header("Publication Analysis")

publication_df = filtered_df[
    filtered_df["Publish_Year"].notna()
].copy()


fig_publication = px.histogram(
    publication_df,
    x="Publish_Year",
    nbins=30,
    title="Distribution of Publication Years"
)

fig_publication.update_layout(
    xaxis_title="Publication Year",
    yaxis_title="Number of Books"
)

st.plotly_chart(
    fig_publication,
    use_container_width=True
)

# BOOK EXPLORER

st.header("📖 Book Explorer")

search = st.text_input(
    "Search by title or author"
)

book_view = filtered_df.copy()

if search:

    mask = (
        book_view["Title"]
        .fillna("")
        .str.contains(
            search,
            case=False,
            na=False
        )
        |
        book_view["Author"]
        .fillna("")
        .str.contains(
            search,
            case=False,
            na=False
        )
    )

    book_view = book_view[mask]


display_columns = [
    "BookID",
    "Title",
    "Author",
    "Language",
    "Status",
    "Reading_Year",
    "Publish_Year",
    "Publisher"
]

st.dataframe(
    book_view[display_columns],
    use_container_width=True,
    hide_index=True
)

# FOOTER

st.divider()

st.caption(
    "Reading Analytics Dashboard • "
    "Python • Pandas • Streamlit • Plotly • Google Sheets"
)
