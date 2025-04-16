# app.py – Enhanced Dashboard With Tab Categorization and Filters
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="E-Commerce Sales Decline Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("e-commerce.csv")

    #df = pd.read_csv("/Users/tharunmk/Downloads/e-commerce.csv")
    df['Visit_Date'] = pd.to_datetime(df['Visit_Date'])
    df['Visit_Month_Full'] = df['Visit_Date'].dt.to_period('M').astype(str)
    return df

df = load_data()

# Handle outliers for key numeric columns
for col in ['Total_Spend', 'Conversion_Rate', 'Bounce_Rate', 'Product_Satisfaction']:
    if col in df.columns:
        q1 = df[col].quantile(0.01)
        q99 = df[col].quantile(0.99)
        df[col] = df[col].clip(lower=q1, upper=q99)

# Month Filter
six_months = ['2023-09', '2023-10', '2023-11', '2023-12', '2024-01', '2024-02']
month_display = ['September 2023', 'October 2023', 'November 2023', 'December 2023', 'January 2024', 'February 2024']
month_map = dict(zip(month_display, six_months))

month_display = ['September 2023', 'October 2023', 'November 2023', 'December 2023', 'January 2024', 'February 2024']
month_map = dict(zip(month_display, six_months))

with st.expander("📅 Filter Visualization by Month"):
    selected_display = st.multiselect("Select Months", month_display, default=month_display, key="filter_overview")
    selected_months = [month_map[m] for m in selected_display]
    df_6mo = df[df['Visit_Month_Full'].isin(selected_months)].copy()

# Metric Calculations
total_unique = df_6mo['Customer_ID'].nunique()
repeat_count = df_6mo[df_6mo['Days_Since_Last_Visit'] <= 20]['Customer_ID'].nunique()
churn_count = df_6mo[df_6mo['Days_Since_Last_Visit'] > 30]['Customer_ID'].nunique()
loyal_count = df_6mo[(df_6mo['Days_Since_Last_Visit'] >= 10) & (df_6mo['Days_Since_Last_Visit'] <= 20)]['Customer_ID'].nunique()
unsat_count = df_6mo[df_6mo['Product_Satisfaction'] <= 2]['Customer_ID'].nunique()

repeat_rate = repeat_count / total_unique * 100
churn_rate = churn_count / total_unique * 100
unsat_rate = unsat_count / total_unique * 100

# Sales Decline Calculation
prev_months = df[~df['Visit_Month_Full'].isin(six_months)]
avg_prev_sales = prev_months['Total_Spend'].sum() / len(prev_months['Visit_Month_Full'].unique())
total_sales_6mo = df_6mo['Total_Spend'].sum()
expected_sales = avg_prev_sales * 6
decline_amount = expected_sales - total_sales_6mo
decline_percent = decline_amount / expected_sales * 100

# Tabs
st.title("📊 E-Commerce Sales Dashboard")
tabs = st.tabs(["📌 Overview", "📈 Sales Performance", "👥 Customer & Geo Insights"])

with tabs[0]:
    st.header("🔍 Executive Overview")

    # Line Chart: 2-Year Sales Trend
    trend_all = df.groupby("Visit_Month_Full")["Total_Spend"].sum().reset_index()
    # (Moved to Tab 1)
# fig_trend = px.line(trend_all, x='Visit_Month_Full', y='Total_Spend', title="🗓️ Total Monthly Sales (2 Years)", markers=True)
    # st.plotly_chart(fig_trend, use_container_width=True)

    # Key Metrics
    st.markdown("### 📋 Performance Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Sales (2 Years)", f"${df['Total_Spend'].sum():,.2f}")
    col2.metric("🔁 Repeat Customers", "39.01%")
    col3.metric("⚠️ Churn Risk", "33.46%")
    col4.metric("🔆 Loyal Customers", "32.49%")

    col5, col6 = st.columns(2)
    col5.metric("😠 Unsatisfied Customers", "20.14%")
    col6.metric("🔻 Decline in Last 6M", f"-${decline_amount:,.2f}", delta=f"-{decline_percent:.2f}%", delta_color="inverse")

with tabs[1]:
    st.header("📈 Sales Performance")

    with st.expander("📅 Filter Visualization by Month"):
        selected_display = st.multiselect("Select Months", month_display, default=month_display, key="filter_sales")
        selected_months = [month_map[m] for m in selected_display]
        df_6mo = df[df['Visit_Month_Full'].isin(selected_months)].copy()

    # Metrics Based on Calculated Values from Full Dataset
    repeat_all = df[df['Days_Since_Last_Visit'] <= 20]['Customer_ID'].nunique()
    churn_all = df[df['Days_Since_Last_Visit'] > 30]['Customer_ID'].nunique()
    loyal_all = df[(df['Days_Since_Last_Visit'] >= 10) & (df['Days_Since_Last_Visit'] <= 20)]['Customer_ID'].nunique()
    unsat_all = df[df['Product_Satisfaction'] <= 2]['Customer_ID'].nunique()
    total_unique_all = df['Customer_ID'].nunique()
    
    st.subheader("📊 Root Cause Analysis (Last 6 Months)")
    st.markdown("""
    - **Customers are not returning**: Increase in churn and decrease in repeat visitors.
    - **Marketing campaigns are underperforming**: Lower conversion, especially in rural zones.
    - **Product targeting issues**: Satisfaction is lower in certain product categories.
    - **Website UX issues**: Bounce rate vs. satisfaction trends show poor site experience.
    """)

    # Line Chart: 2-Year Sales Trend
    trend_all = df.groupby("Visit_Month_Full")["Total_Spend"].sum().reset_index()
    fig_trend = px.line(trend_all, x='Visit_Month_Full', y='Total_Spend', title="🗓️ Total Monthly Sales (2 Years)", markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)

    sales_trend = df_6mo.groupby('Visit_Month_Full')['Total_Spend'].sum().reset_index()
    fig1 = px.line(sales_trend, x='Visit_Month_Full', y='Total_Spend', title="📉 Monthly Sales Trend", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("🔁 Monthly Repeat vs Churn")
    behavior_trend = df_6mo.copy()
    behavior_trend['Type'] = np.where(behavior_trend['Days_Since_Last_Visit'] <= 20, 'Repeat',
                            np.where(behavior_trend['Days_Since_Last_Visit'] > 30, 'Churn', 'Other'))
    bar_data = behavior_trend.groupby(['Visit_Month_Full', 'Type'])['Customer_ID'].nunique().reset_index()
    fig7 = px.bar(bar_data, x='Visit_Month_Full', y='Customer_ID', color='Type', barmode='stack',
                    title="Customer Return Behavior by Month",
                    labels={"Visit_Month_Full": "Month", "Customer_ID": "Customer Count"})
    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("📈 Metric Trends Over Time")
    metric_trend = df.copy()
    metric_trend['Repeat'] = metric_trend['Days_Since_Last_Visit'] <= 20
    metric_trend['Churn'] = metric_trend['Days_Since_Last_Visit'] > 30
    metric_trend['Loyal'] = metric_trend['Days_Since_Last_Visit'].between(10, 20)
    metric_trend['Unsatisfied'] = metric_trend['Product_Satisfaction'] <= 2

    metric_summary = metric_trend.groupby('Visit_Month_Full').agg({
        'Customer_ID': 'nunique',
        'Repeat': 'sum',
        'Churn': 'sum',
        'Loyal': 'sum',
        'Unsatisfied': 'sum'
    }).reset_index()
    metric_summary['Repeat_Rate'] = metric_summary['Repeat'] / metric_summary['Customer_ID'] * 100
    metric_summary['Churn_Rate'] = metric_summary['Churn'] / metric_summary['Customer_ID'] * 100
    metric_summary['Loyal_Rate'] = metric_summary['Loyal'] / metric_summary['Customer_ID'] * 100
    metric_summary['Unsatisfied_Rate'] = metric_summary['Unsatisfied'] / metric_summary['Customer_ID'] * 100

    metric_melted = metric_summary.melt(id_vars='Visit_Month_Full',
        value_vars=['Repeat_Rate', 'Churn_Rate', 'Loyal_Rate', 'Unsatisfied_Rate'],
        var_name='Metric', value_name='Rate')

    fig_metric = px.line(metric_melted, x='Visit_Month_Full', y='Rate', color='Metric',
                         markers=True, title="📊 Monthly Trend: Repeat, Churn, Loyalty, Unsatisfaction",
                         labels={"Visit_Month_Full": "Month", "Rate": "Percentage"})
    st.plotly_chart(fig_metric, use_container_width=True)

with tabs[2]:
    st.header("👥 Customer Behavior & Geographic Insights")

    st.subheader("📊 Product Category Sales")
    cat_sales = df_6mo.groupby("Product_Category")['Total_Spend'].sum().reset_index()
    fig2 = px.bar(cat_sales, x='Product_Category', y='Total_Spend', color='Total_Spend', color_continuous_scale='Aggrnyl', labels={"Product_Category": "Product Category", "Total_Spend": "Total Revenue"})
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📉 Satisfaction by Category")
    fig3 = px.violin(df_6mo, x='Product_Category', y='Product_Satisfaction', color='Product_Category', box=True, points='all', labels={"Product_Category": "Product Category", "Product_Satisfaction": "Customer Satisfaction"})
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("📍 Sales by City")
    city_sales = df_6mo.groupby("City")['Total_Spend'].mean().reset_index()
    fig4 = px.funnel(city_sales.sort_values('Total_Spend', ascending=False), x='Total_Spend', y='City', title="Avg Spend by City", labels={"Total_Spend": "Average Revenue", "City": "City"})
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("🧍‍♂️ Customer Segments")
    segment_data = pd.Series({
    'Churn (>30d)': churn_count,
    'Loyal (10–30d)': loyal_count,
    'Unsatisfied (≤2)': unsat_count,
    'Other': total_unique - (churn_count + loyal_count + unsat_count)
})
    fig5 = px.pie(values=segment_data.values, names=segment_data.index, title="Customer Segmentation", hole=0.4)
    fig5.update_traces(textinfo='percent+label')
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("📈 Conversion Rate by City Type")
    if 'Conversion_Rate' in df_6mo.columns and 'City_Type' in df_6mo.columns:
        fig_conv = px.strip(df_6mo, x='City_Type', y='Conversion_Rate', color='City_Type', title="Conversion Rate Spread by City Type", stripmode='overlay', labels={"City_Type": "City Type", "Conversion_Rate": "Conversion Rate (%)"})
        st.plotly_chart(fig_conv, use_container_width=True)

    st.subheader("📊 Bounce Rate by Month")
    if 'Bounce_Rate' in df_6mo.columns:
        fig_bounce = px.box(df_6mo, x='Visit_Month_Full', y='Bounce_Rate', color='Visit_Month_Full', title="Monthly Bounce Rate Trends", labels={"Visit_Month_Full": "Month", "Bounce_Rate": "Bounce Rate (%)"})
        st.plotly_chart(fig_bounce, use_container_width=True)

    st.subheader("📦 Items vs Spend")
    if 'Num_Items' in df_6mo.columns:
        fig9 = px.density_contour(df_6mo, x='Num_Items', y='Total_Spend', title='Item Count vs Spend Density', labels={"Num_Items": "Number of Items Purchased", "Total_Spend": "Total Spend"})
        st.plotly_chart(fig9, use_container_width=True)

    st.subheader("🌆 Avg Spend by City Type")
    if 'City_Type' in df_6mo.columns:
        citytype_spend = df_6mo.groupby('City_Type')['Total_Spend'].mean().reset_index()
        fig10 = px.bar(citytype_spend, x='City_Type', y='Total_Spend', color='City_Type', title="Average Spend Across City Types", labels={"City_Type": "City Type", "Total_Spend": "Average Spend"})
        st.plotly_chart(fig10, use_container_width=True)


