# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="Import-Export Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Page background color and custom CSS
page_bg_color = """
    <style>
    body {
        background-color: #e8f5e9;
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
    }
    .metric-box {
        padding: 15px;
        margin: 5px;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-title {
        font-size: 16px;
        font-weight: bold;
        color: #333333;
    }
    .metric-value {
        font-size: 20px;
        color: #007bff;
    }
    .metric-delta {
        color: #ff6b6b;
    }
    </style>
"""
st.markdown(page_bg_color, unsafe_allow_html=True)

# Load data
df = pd.read_csv("Imports_Exports_Dataset.csv")  # Adjust the file path accordingly

# Sidebar
with st.sidebar:
    st.title('📦 Import-Export Dashboard')

# Filter by year
df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
year_list = sorted(df['Date'].dt.year.unique(), reverse=True)
selected_year = st.selectbox('Select a year', year_list)

# Filter data based on the selected year
df_selected_year = df[df['Date'].dt.year == selected_year]

# Multi-select for country
country_list = df['Country'].unique()
selected_countries = st.multiselect('Select country(s)', country_list, default=country_list[:3])

if selected_countries:
    df_selected_year = df_selected_year[df_selected_year['Country'].isin(selected_countries)]

# Select color theme
color_theme_list = ['blues', 'reds', 'greens', 'turbo', 'viridis']
selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

# Helper Functions
def format_value(val):
    return f"${val / 1e6:.1f}M" if val > 1e6 else f"${val / 1e3:.1f}K"

def calculate_transaction_difference(input_df, input_year):
    selected_year_data = input_df[input_df['Date'].dt.year == input_year].reset_index()
    previous_year_data = input_df[input_df['Date'].dt.year == input_year - 1].reset_index()
    selected_year_data['value_difference'] = selected_year_data.Value.sub(previous_year_data.Value, fill_value=0)
    return pd.concat([selected_year_data.Country, selected_year_data.Value, selected_year_data.value_difference], axis=1).sort_values(by="value_difference", ascending=False)

# Dashboard Main Panel
st.markdown("<h1 style='text-align: center; color: #004d40;'>📦 Import-Export Transactions Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #004d40;'>Comprehensive analysis of global trade flows by year and country</h4>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# Display key metrics in card layout
df_transaction_diff_sorted = calculate_transaction_difference(df, selected_year)

first_country = df_transaction_diff_sorted.Country.iloc[0] if selected_year > df['Date'].dt.year.min() else '-'
first_country_value = format_value(df_transaction_diff_sorted.Value.iloc[0])
first_country_delta = format_value(df_transaction_diff_sorted.value_difference.iloc[0]) if selected_year > df['Date'].dt.year.min() else '-'

last_country = df_transaction_diff_sorted.Country.iloc[-1] if selected_year > df['Date'].dt.year.min() else '-'
last_country_value = format_value(df_transaction_diff_sorted.Value.iloc[-1])
last_country_delta = format_value(df_transaction_diff_sorted.value_difference.iloc[-1]) if selected_year > df['Date'].dt.year.min() else '-'

# Metrics in a card layout
st.markdown(f"""
<div class='metric-container'>
    <div class='metric-box'>
        <div class='metric-title'>Top Country by Value</div>
        <div class='metric-value'>{first_country}</div>
        <div class='metric-delta'>Difference: {first_country_delta}</div>
    </div>
    <div class='metric-box'>
        <div class='metric-title'>Lowest Country by Value</div>
        <div class='metric-value'>{last_country}</div>
        <div class='metric-delta'>Difference: {last_country_delta}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Insights Section
st.markdown("### Key Insights:")
insight_1 = f"*Top Country*: {first_country} had the highest transaction value of {first_country_value}, reflecting its dominance in the selected trade data."
insight_2 = f"*Bottom Country*: {last_country} had the lowest transaction value of {last_country_value}, indicating it contributed less to the overall trade."
st.write(insight_1)
st.write(insight_2)

# Additional Graphs Section
col1, col2 = st.columns(2)

# Scatter Plot for Country-wise Transaction Value
with col1:
    st.markdown('#### Scatter Plot: Country-wise Transaction Value')
    scatter_plot = px.scatter(df_selected_year, x='Country', y='Value', color='Category',
                              size='Value', title="Scatter Plot of Transaction Value by Country",
                              color_discrete_sequence=px.colors.sequential.Viridis)
    st.plotly_chart(scatter_plot, use_container_width=True)

# Box Plot for Transaction Value Distribution by variable
with col2:
    st.markdown('#### Box Plot: Transaction Value Distribution by Variable')
    
    # Allow user to choose x and y for boxplot
    variable_x = st.selectbox('Select X-axis variable', ['Category', 'Country'])
    variable_y = st.selectbox('Select Y-axis variable', ['Value', 'Date'])

    box_plot = px.box(df_selected_year, x=variable_x, y=variable_y, color=variable_x,
                      title=f"Box Plot: {variable_y} Distribution by {variable_x}",
                      color_discrete_sequence=px.colors.sequential.Turbo)
    st.plotly_chart(box_plot, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Heatmap for Correlation
st.markdown('#### Heatmap: Correlation Matrix')
if 'Value' in df_selected_year.columns and 'Date' in df_selected_year.columns:
    # Filter numeric columns for correlation
    df_selected_year['Date_Ordinal'] = df_selected_year['Date'].apply(lambda x: x.toordinal())
    numeric_df = df_selected_year[['Value', 'Date_Ordinal']]
    
    # Create heatmap using Seaborn
    fig, ax = plt.subplots()
    correlation_matrix = numeric_df.corr()
    sns.heatmap(correlation_matrix, annot=True, cmap=selected_color_theme, ax=ax)
    st.pyplot(fig)

# Donut Chart for Value Distribution by Category
st.markdown('#### Donut Chart for Value Distribution by Category')
donut_chart = px.pie(df_selected_year, values='Value', names='Category', hole=0.4,
                     title="Value Distribution by Category", color_discrete_sequence=px.colors.sequential.RdBu)
st.plotly_chart(donut_chart, use_container_width=True)

# Line Chart for Transactions Over Time
st.markdown('#### Transactions Over Time')
line_chart = alt.Chart(df_selected_year).mark_line().encode(
    x=alt.X('Date:T', axis=alt.Axis(title='Date')),
    y=alt.Y('Value:Q', axis=alt.Axis(title='Transaction Value')),
    color=alt.Color('Category:N', legend=alt.Legend(title="Category"))
).properties(width=900, height=300)
st.altair_chart(line_chart, use_container_width=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("##### Created by Your Name | Import-Export Dashboard © 2024", unsafe_allow_html=True)
