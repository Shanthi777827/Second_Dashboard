import pandas as pd
import streamlit as st
import plotly.express as px

# Page settings
st.set_page_config(
    page_title="Ride Operations Dashboard",
    layout="wide"
)

# Reduce KPI value size so long values are fully visible
st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 28px;
}
</style>
""", unsafe_allow_html=True)

# Dashboard title
st.title("Ride Operations & Performance Dashboard")
st.write(
    "Overview of ride volume, revenue, operational performance and customer experience"
)

st.markdown("---")


# Load data
file_path = "/Users/marrow/Downloads/Database Set.xlsx - Sheet1.csv"

df = pd.read_csv(file_path)


# Clean date column
df["Date & Time"] = pd.to_datetime(
    df["Date & Time"],
    errors="coerce"
)


# Clean text columns
text_columns = [
    "City",
    "Vehicle Type",
    "Payment Method",
    "Ride Status",
    "Driver Education Qualification"
]

for column in text_columns:
    df[column] = (
        df[column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
    )


# Clean numeric columns
numeric_columns = [
    "Distance (km)",
    "Duration (min)",
    "Fare (INR)",
    "Revenue (INR)",
    "Customer Rating",
    "Fare per KM (auto QC)"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# Sidebar filters
st.sidebar.header("Filters")


# Date filter
minimum_date = df["Date & Time"].min().date()
maximum_date = df["Date & Time"].max().date()

selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date
)


# City filter
city_options = sorted(df["City"].unique())

selected_city = st.sidebar.selectbox(
    "City",
    ["All"] + city_options
)


# Vehicle filter
vehicle_options = sorted(df["Vehicle Type"].unique())

selected_vehicle = st.sidebar.selectbox(
    "Vehicle Type",
    ["All"] + vehicle_options
)


# Payment filter
payment_options = sorted(df["Payment Method"].unique())

selected_payment = st.sidebar.selectbox(
    "Payment Method",
    ["All"] + payment_options
)


# Ride status filter
status_options = sorted(df["Ride Status"].unique())

selected_status = st.sidebar.selectbox(
    "Ride Status",
    ["All"] + status_options
)


# Driver education filter
education_options = sorted(
    df["Driver Education Qualification"].unique()
)

selected_education = st.sidebar.selectbox(
    "Driver Education",
    ["All"] + education_options
)


# Apply filters
filtered_df = df.copy()


# Date filter
if len(selected_dates) == 2:

    start_date = pd.to_datetime(selected_dates[0])

    end_date = (
        pd.to_datetime(selected_dates[1])
        + pd.Timedelta(days=1)
    )

    filtered_df = filtered_df[
        (filtered_df["Date & Time"] >= start_date)
        & (filtered_df["Date & Time"] < end_date)
    ]


# City filter
if selected_city != "All":

    filtered_df = filtered_df[
        filtered_df["City"] == selected_city
    ]


# Vehicle filter
if selected_vehicle != "All":

    filtered_df = filtered_df[
        filtered_df["Vehicle Type"] == selected_vehicle
    ]


# Payment filter
if selected_payment != "All":

    filtered_df = filtered_df[
        filtered_df["Payment Method"] == selected_payment
    ]


# Ride status filter
if selected_status != "All":

    filtered_df = filtered_df[
        filtered_df["Ride Status"] == selected_status
    ]


# Education filter
if selected_education != "All":

    filtered_df = filtered_df[
        filtered_df["Driver Education Qualification"]
        == selected_education
    ]


# Stop if no data matches filters
if filtered_df.empty:

    st.warning("No data matches the selected filters.")

    st.stop()


# Completed rides
completed_df = filtered_df[
    filtered_df["Ride Status"].str.lower() == "completed"
]


# KPI calculations
total_rides = len(filtered_df)

completed_rides = len(completed_df)

completion_rate = (
    completed_rides / total_rides * 100
    if total_rides > 0
    else 0
)

total_revenue = filtered_df["Revenue (INR)"].sum()

average_rating = completed_df["Customer Rating"].mean()

if pd.notna(average_rating):

    rating_display = f"{average_rating:.2f}"

else:

    rating_display = "—"


# KPI section
st.subheader("Key Performance Indicators")


kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)


# Total rides
with kpi1:

    with st.container(border=True):

        st.metric(
            "Total Rides",
            f"{total_rides:,}"
        )


# Completed rides
with kpi2:

    with st.container(border=True):

        st.metric(
            "Completed Rides",
            f"{completed_rides:,}"
        )


# Completion rate
with kpi3:

    with st.container(border=True):

        st.metric(
            "Completion Rate",
            f"{completion_rate:.1f}%"
        )


# Total revenue
with kpi4:

    with st.container(border=True):

        st.metric(
            "Total Revenue",
            f"₹{total_revenue:,.0f}"
        )


# Average rating
with kpi5:

    with st.container(border=True):

        st.metric(
            "Average Customer Rating",
            rating_display
        )


st.markdown("---")


# Ride Status Summary
st.subheader("Ride Status Summary")


ride_status_table = (
    filtered_df["Ride Status"]
    .value_counts()
    .reset_index()
)

ride_status_table.columns = [
    "Ride Status",
    "Ride Count"
]


with st.container(border=True):

    st.dataframe(
        ride_status_table,
        use_container_width=True,
        hide_index=True
    )


# City Performance Summary
st.subheader("City Performance Summary")


city_summary = (
    filtered_df
    .groupby("City")
    .agg(
        Rides=("Ride ID", "count"),
        Revenue=("Revenue (INR)", "sum")
    )
    .reset_index()
    .sort_values(
        "Revenue",
        ascending=False
    )
)


city_summary_display = city_summary.copy()

city_summary_display["Revenue"] = (
    city_summary_display["Revenue"]
    .map(lambda x: f"₹{x:,.0f}")
)


with st.container(border=True):

    st.dataframe(
        city_summary_display,
        use_container_width=True,
        hide_index=True
    )


st.markdown("---")


# Revenue by City
st.subheader("Revenue by City")


city_revenue = (
    filtered_df
    .groupby("City", as_index=False)["Revenue (INR)"]
    .sum()
    .sort_values(
        "Revenue (INR)",
        ascending=False
    )
)


fig_city_revenue = px.bar(
    city_revenue,
    x="City",
    y="Revenue (INR)",
    text="Revenue (INR)"
)


fig_city_revenue.update_traces(
    texttemplate="₹%{text:,.0f}",
    textposition="outside"
)


fig_city_revenue.update_layout(
    showlegend=False,
    xaxis_title="City",
    yaxis_title="Revenue (INR)",
    height=450
)


st.plotly_chart(
    fig_city_revenue,
    use_container_width=True
)


# Revenue by Vehicle Type
st.subheader("Revenue by Vehicle Type")


vehicle_revenue = (
    filtered_df
    .groupby(
        "Vehicle Type",
        as_index=False
    )["Revenue (INR)"]
    .sum()
    .sort_values(
        "Revenue (INR)",
        ascending=False
    )
)


fig_vehicle_revenue = px.bar(
    vehicle_revenue,
    x="Vehicle Type",
    y="Revenue (INR)",
    text="Revenue (INR)"
)


fig_vehicle_revenue.update_traces(
    texttemplate="₹%{text:,.0f}",
    textposition="outside"
)


fig_vehicle_revenue.update_layout(
    showlegend=False,
    xaxis_title="Vehicle Type",
    yaxis_title="Revenue (INR)",
    height=450
)


st.plotly_chart(
    fig_vehicle_revenue,
    use_container_width=True
)


# Customer Rating by Vehicle Type
st.subheader("Customer Rating by Vehicle Type")


rating_vehicle = (
    completed_df
    .groupby(
        "Vehicle Type",
        as_index=False
    )["Customer Rating"]
    .mean()
    .sort_values(
        "Customer Rating",
        ascending=False
    )
)


fig_rating = px.bar(
    rating_vehicle,
    x="Vehicle Type",
    y="Customer Rating",
    text="Customer Rating"
)


fig_rating.update_traces(
    texttemplate="%{text:.2f}",
    textposition="outside"
)


fig_rating.update_layout(
    showlegend=False,
    xaxis_title="Vehicle Type",
    yaxis_title="Average Customer Rating",
    yaxis=dict(range=[0, 5.5]),
    height=450
)


st.plotly_chart(
    fig_rating,
    use_container_width=True
)


# Distance vs Revenue
st.subheader("Distance vs Revenue")


scatter_data = filtered_df[
    [
        "Distance (km)",
        "Revenue (INR)",
        "Vehicle Type",
        "City",
        "Ride Status"
    ]
].dropna()


fig_scatter = px.scatter(
    scatter_data,
    x="Distance (km)",
    y="Revenue (INR)",
    color="Vehicle Type",
    hover_data=[
        "City",
        "Ride Status"
    ],
    opacity=0.65
)


fig_scatter.update_layout(
    xaxis_title="Distance (km)",
    yaxis_title="Revenue (INR)",
    height=500
)


st.plotly_chart(
    fig_scatter,
    use_container_width=True
)


# Statistical Analysis
st.subheader("Statistical Analysis")


correlation_columns = [
    "Distance (km)",
    "Duration (min)",
    "Fare (INR)",
    "Revenue (INR)",
    "Customer Rating",
    "Fare per KM (auto QC)"
]


correlation_data = filtered_df[
    correlation_columns
].corr()


fig_heatmap = px.imshow(
    correlation_data,
    text_auto=".2f",
    aspect="auto",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1
)


fig_heatmap.update_layout(
    height=600
)


st.plotly_chart(
    fig_heatmap,
    use_container_width=True
)