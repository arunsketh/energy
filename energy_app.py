import streamlit as st
import pandas as pd
import altair as alt

def calculate_yearly_cost(day_units_month, night_units_month, day_rate_p, night_rate_p, standing_charge_p):
    """
    Calculates the estimated total yearly electricity cost including VAT.

    Args:
        day_units_month (float): Monthly electricity consumption during the day in kWh.
        night_units_month (float): Monthly electricity consumption at night in kWh.
        day_rate_p (float): Cost per kWh during the day in pence.
        night_rate_p (float): Cost per kWh at night in pence.
        standing_charge_p (float): Daily standing charge in pence.

    Returns:
        float: The total estimated yearly cost in pounds (£).
    """
    # Constants
    MONTHS_IN_YEAR = 12
    AVG_DAYS_IN_YEAR = 365.25
    VAT_RATE = 1.05  # 5% VAT

    # Calculate annual consumption
    yearly_day_units = day_units_month * MONTHS_IN_YEAR
    yearly_night_units = night_units_month * MONTHS_IN_YEAR

    # Calculate cost components in pence
    yearly_day_cost_p = yearly_day_units * day_rate_p
    yearly_night_cost_p = yearly_night_units * night_rate_p
    yearly_standing_cost_p = standing_charge_p * AVG_DAYS_IN_YEAR

    # Calculate total cost before VAT
    total_cost_before_vat_p = yearly_day_cost_p + yearly_night_cost_p + yearly_standing_cost_p

    # Add VAT and convert to pounds
    total_yearly_cost_pounds = (total_cost_before_vat_p * VAT_RATE) / 100

    return total_yearly_cost_pounds

# --- Page Configuration ---
st.set_page_config(
    page_title="Electricity Tariff Comparator",
    page_icon="💡",
    layout="wide"
)

# --- App Title ---
st.title("💡 Electricity Tariff Comparison Tool")
st.markdown("Enter your current tariff details and monthly consumption to see how it compares to other plans.")

# --- Data for Comparison Tariffs ---
# This data is based on the spreadsheet provided in the prompt.
data = {
    'Supplier': ['OVO', 'Fuse 1', 'Fuse 2', 'Fuse 3', 'OVO Simpler', 'Octopus', 'Fuse 4'],
    'Day Rate (p/kWh)': [22.21, 25.24, 24.65, 24.91, 27.4, 31.05, 21.9],
    'Night Rate (p/kWh)': [15.8, 17.64, 24.65, 17.59, 19.48, 13.79, 21.9],
    'Standing Charge (p/day)': [57.74, 42.4, 47.94, 40.3, 50.5, 49.54, 47.04]
}
tariffs_df = pd.DataFrame(data)


# --- Sidebar for User Inputs ---
st.sidebar.header("Your Details")
st.sidebar.markdown("👇 Enter your details below.")

# User consumption inputs
st.sidebar.subheader("Monthly Consumption (kWh)")
day_consumption = st.sidebar.number_input("Day Units (kWh)", min_value=0, value=392, step=10)
night_consumption = st.sidebar.number_input("Night Units (kWh)", min_value=0, value=49, step=10)

# User's current tariff inputs
st.sidebar.subheader("Your Current Tariff")
current_day_rate = st.sidebar.number_input("Day Rate (p/kWh)", min_value=0.0, value=22.21, step=0.1, format="%.2f")
current_night_rate = st.sidebar.number_input("Night Rate (p/kWh)", min_value=0.0, value=15.80, step=0.1, format="%.2f")
current_standing_charge = st.sidebar.number_input("Standing Charge (p/day)", min_value=0.0, value=57.74, step=0.1, format="%.2f")


# --- Main Panel for Results ---

# --- Calculations ---
# Calculate cost for the user's current tariff
current_tariff_cost = calculate_yearly_cost(
    day_consumption,
    night_consumption,
    current_day_rate,
    current_night_rate,
    current_standing_charge
)

# Calculate costs for all comparison tariffs
tariffs_df['Estimated Yearly Cost (£)'] = tariffs_df.apply(
    lambda row: calculate_yearly_cost(
        day_consumption,
        night_consumption,
        row['Day Rate (p/kWh)'],
        row['Night Rate (p/kWh)'],
        row['Standing Charge (p/day)']
    ),
    axis=1
)

# Create a DataFrame for the user's current tariff to add to the chart
current_tariff_data = pd.DataFrame({
    'Supplier': ['Your Current Tariff'],
    'Estimated Yearly Cost (£)': [current_tariff_cost]
})

# Combine the user's tariff with the comparison tariffs
all_tariffs_for_chart = pd.concat([current_tariff_data, tariffs_df[['Supplier', 'Estimated Yearly Cost (£)']]], ignore_index=True)


# --- Display Results ---
st.header("Results")

# Display the calculated cost for the user's current tariff
st.metric(label="Your Estimated Yearly Cost", value=f"£{current_tariff_cost:,.2f}")

st.markdown("---")

# --- Comparison Chart ---
st.subheader("Yearly Cost Comparison")

# Create a bar chart using Altair for better customization
chart = alt.Chart(all_tariffs_for_chart).mark_bar().encode(
    x=alt.X('Supplier:N', sort='-y', title='Supplier'),
    y=alt.Y('Estimated Yearly Cost (£):Q', title='Estimated Yearly Cost (£)'),
    color=alt.condition(
        alt.datum.Supplier == 'Your Current Tariff',
        alt.value('orange'),  # Highlight color for the user's tariff
        alt.value('steelblue') # Default color for other tariffs
    ),
    tooltip=[
        alt.Tooltip('Supplier', title='Supplier'),
        alt.Tooltip('Estimated Yearly Cost (£)', title='Yearly Cost', format='£,.2f')
    ]
).properties(
    height=400
)

st.altair_chart(chart, use_container_width=True)


# --- Data Table ---
st.subheader("Comparison Tariff Details")
st.markdown("Here are the details of the tariffs used in the comparison, along with their calculated yearly costs based on your consumption.")

# Format the cost column to show as currency
display_df = tariffs_df.copy()
display_df['Estimated Yearly Cost (£)'] = display_df['Estimated Yearly Cost (£)'].apply(lambda x: f"£{x:,.2f}")
st.dataframe(display_df, use_container_width=True)

