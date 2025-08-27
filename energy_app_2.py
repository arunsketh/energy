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

# --- Initialize Session State ---
# This is crucial for storing custom tariffs added by the user.
if 'custom_tariffs' not in st.session_state:
    st.session_state.custom_tariffs = []


# --- App Title ---
st.title("💡 Electricity Tariff Comparison Tool")
st.markdown("Enter your current tariff details and monthly consumption to see how it compares to other plans.")

st.markdown("---")

# --- User Inputs on Main Page ---
st.header("Your Details")
st.markdown("👇 Enter your details below to see the comparison.")

col1, col2 = st.columns(2)

with col1:
    # User consumption inputs
    st.subheader("Monthly Consumption (kWh)")
    day_consumption = st.number_input("Day Units (kWh)", min_value=0, value=392, step=10)
    night_consumption = st.number_input("Night Units (kWh)", min_value=0, value=49, step=10)

with col2:
    # User's current tariff inputs
    st.subheader("Your Current Tariff")
    current_day_rate = st.number_input("Day Rate (p/kWh)", min_value=0.0, value=22.21, step=0.1, format="%.2f")
    current_night_rate = st.number_input("Night Rate (p/kWh)", min_value=0.0, value=15.80, step=0.1, format="%.2f")
    current_standing_charge = st.number_input("Standing Charge (p/day)", min_value=0.0, value=57.74, step=0.1, format="%.2f")

# --- Section to Add New Tariffs ---
with st.expander("➕ Add a Custom Tariff for Comparison"):
    form_col1, form_col2, form_col3, form_col4 = st.columns([2,1,1,1])
    with form_col1:
        new_supplier = st.text_input("Supplier Name")
    with form_col2:
        new_day_rate = st.number_input("Day Rate (p/kWh)", min_value=0.0, step=0.1, format="%.2f", key="new_day")
    with form_col3:
        new_night_rate = st.number_input("Night Rate (p/kWh)", min_value=0.0, step=0.1, format="%.2f", key="new_night")
    with form_col4:
        new_standing_charge = st.number_input("Standing Charge (p/day)", min_value=0.0, step=0.1, format="%.2f", key="new_standing")
    
    if st.button("Add Tariff to Comparison"):
        if new_supplier: # Basic validation to ensure a name is entered
            st.session_state.custom_tariffs.append({
                'Supplier': new_supplier,
                'Day Rate (p/kWh)': new_day_rate,
                'Night Rate (p/kWh)': new_night_rate,
                'Standing Charge (p/day)': new_standing_charge
            })
            st.success(f"Added '{new_supplier}' to the comparison.")
        else:
            st.warning("Please enter a supplier name.")


# --- Data for Comparison Tariffs ---
# This data is based on the spreadsheet provided in the prompt.
data = {
    'Supplier': ['OVO', 'Fuse 1', 'Fuse 2', 'Fuse 3', 'OVO Simpler', 'Octopus', 'Fuse 4'],
    'Day Rate (p/kWh)': [22.21, 25.24, 24.65, 24.91, 27.4, 31.05, 21.9],
    'Night Rate (p/kWh)': [15.8, 17.64, 24.65, 17.59, 19.48, 13.79, 21.9],
    'Standing Charge (p/day)': [57.74, 42.4, 47.94, 40.3, 50.5, 49.54, 47.04]
}
tariffs_df = pd.DataFrame(data)


# --- Calculations ---
# Combine default tariffs with any custom tariffs added by the user
if st.session_state.custom_tariffs:
    custom_tariffs_df = pd.DataFrame(st.session_state.custom_tariffs)
    comparison_df = pd.concat([tariffs_df, custom_tariffs_df], ignore_index=True)
else:
    comparison_df = tariffs_df.copy()


# Calculate cost for the user's current tariff
current_tariff_cost = calculate_yearly_cost(
    day_consumption,
    night_consumption,
    current_day_rate,
    current_night_rate,
    current_standing_charge
)

# Calculate costs for all comparison tariffs
comparison_df['Estimated Yearly Cost (£)'] = comparison_df.apply(
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

# Combine the user's tariff with the comparison tariffs for the chart
all_tariffs_for_chart = pd.concat([current_tariff_data, comparison_df[['Supplier', 'Estimated Yearly Cost (£)']]], ignore_index=True)


# --- Display Results ---
st.markdown("---")
st.header("Results")

# Display the calculated cost for the user's current tariff
st.metric(label="Your Estimated Yearly Cost", value=f"£{current_tariff_cost:,.2f}")


# --- Comparison Chart ---
st.subheader("Yearly Cost Comparison")

# Ensure the dataframe is not empty before trying to render a chart
if not all_tariffs_for_chart.empty:
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
else:
    st.warning("No data available to display the chart.")


# --- Data Table with Color Formatting ---
st.subheader("Comparison Tariff Details")
st.markdown("Here are the details of the tariffs used in the comparison. Cheaper rates are highlighted in green.")

# Attempt to create a styled DataFrame, but handle the ImportError if matplotlib is missing.
try:
    styled_df = comparison_df.style.background_gradient(
        cmap='RdYlGn_r', # Red-Yellow-Green (reversed) so green is low
        subset=['Day Rate (p/kWh)', 'Night Rate (p/kWh)', 'Standing Charge (p/day)', 'Estimated Yearly Cost (£)']
    ).format({
        'Day Rate (p/kWh)': '{:.2f}p',
        'Night Rate (p/kWh)': '{:.2f}p',
        'Standing Charge (p/day)': '{:.2f}p',
        'Estimated Yearly Cost (£)': '£{:.2f}'
    })
    st.dataframe(styled_df, use_container_width=True)
except ImportError:
    st.warning("Could not apply color formatting because the `matplotlib` library is not installed. Displaying the raw data table instead.")
    st.info("To enable color formatting for a deployed app, add `matplotlib` to your `requirements.txt` file.")
    # Display the unformatted dataframe as a fallback
    st.dataframe(comparison_df.style.format({
        'Day Rate (p/kWh)': '{:.2f}p',
        'Night Rate (p/kWh)': '{:.2f}p',
        'Standing Charge (p/day)': '{:.2f}p',
        'Estimated Yearly Cost (£)': '£{:.2f}'
    }), use_container_width=True)
except Exception as e:
    st.error(f"An unexpected error occurred while styling the table: {e}")
    st.dataframe(comparison_df, use_container_width=True) # Display raw data on other errors
