import streamlit as st
import pandas as pd

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
st.header("💡 Electricity Tariff Comparison Tool")
st.markdown("Enter your tariff details and monthly consumption to compare plans.")

st.markdown("---")

# --- User Inputs and Results on Main Page ---
col1, col2, col3 = st.columns([1.5, 1.5, 3])

with col1:
    # User consumption inputs
    st.subheader("Your Details")
    day_consumption = st.number_input("Monthly Day Units (kWh)", min_value=0, value=392, step=10)
    night_consumption = st.number_input("Monthly Night Units (kWh)", min_value=0, value=49, step=10)
    
    st.markdown("###### Your Current Tariff")
    current_day_rate = st.number_input("Day Rate (p)", min_value=0.0, value=22.21, step=0.1, format="%.2f")
    current_night_rate = st.number_input("Night Rate (p)", min_value=0.0, value=15.80, step=0.1, format="%.2f")
    current_standing_charge = st.number_input("Standing (p/day)", min_value=0.0, value=57.74, step=0.1, format="%.2f")

with col2:
    # Section to Add New Tariffs
    st.subheader("Add Custom Tariff")
    new_supplier = st.text_input("Supplier Name")
    new_tariff_type = st.text_input("Tariff Type (e.g., Standard, E7)")
    new_day_rate = st.number_input("Day Rate (p)", min_value=0.0, step=0.1, format="%.2f", key="new_day")
    new_night_rate = st.number_input("Night Rate (p)", min_value=0.0, step=0.1, format="%.2f", key="new_night")
    new_standing_charge = st.number_input("Standing (p/day)", min_value=0.0, step=0.1, format="%.2f", key="new_standing")
    
    if st.button("Add Tariff"):
        if new_supplier: # Basic validation to ensure a name is entered
            st.session_state.custom_tariffs.append({
                'Supplier': new_supplier,
                'Tariff Type': new_tariff_type,
                'Day Rate (p/kWh)': new_day_rate,
                'Night Rate (p/kWh)': new_night_rate,
                'Standing Charge (p/day)': new_standing_charge
            })
            st.success(f"Added '{new_supplier}'")
        else:
            st.warning("Please enter a supplier name.")


# --- Data for Comparison Tariffs ---
data = {
    'Supplier': ['OVO', 'Fuse 1', 'Fuse 2', 'Fuse 3', 'OVO Simpler', 'Octopus', 'Fuse 4'],
    'Tariff Type': ['Standard', 'Standard', 'Standard', 'Standard', 'Standard', 'Economy 7', 'Standard'],
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
current_tariff_cost_yearly = calculate_yearly_cost(
    day_consumption,
    night_consumption,
    current_day_rate,
    current_night_rate,
    current_standing_charge
)
current_tariff_cost_monthly = current_tariff_cost_yearly / 12

# Create a DataFrame for the user's current tariff to add to the main table
your_tariff_df = pd.DataFrame([{
    'Supplier': 'Your Current Tariff',
    'Tariff Type': 'Custom',
    'Day Rate (p/kWh)': current_day_rate,
    'Night Rate (p/kWh)': current_night_rate,
    'Standing Charge (p/day)': current_standing_charge,
    'Estimated Yearly Cost (£)': current_tariff_cost_yearly,
    'Estimated Monthly Cost (£)': current_tariff_cost_monthly
}])

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
comparison_df['Estimated Monthly Cost (£)'] = comparison_df['Estimated Yearly Cost (£)'] / 12

# Add the user's tariff to the top of the comparison DataFrame
final_comparison_df = pd.concat([your_tariff_df, comparison_df], ignore_index=True)


# --- Data Table with Color Formatting ---
with col3:
    st.subheader("Comparison Details")
    
    # Attempt to create a styled DataFrame, but handle the ImportError if matplotlib is missing.
    try:
        # Reorder columns for better display
        display_cols = ['Supplier', 'Tariff Type', 'Day Rate (p/kWh)', 'Night Rate (p/kWh)', 'Standing Charge (p/day)', 'Estimated Monthly Cost (£)', 'Estimated Yearly Cost (£)']
        styled_df = final_comparison_df[display_cols].style.background_gradient(
            cmap='RdYlGn_r', # Red-Yellow-Green (reversed) so green is low
            subset=['Day Rate (p/kWh)', 'Night Rate (p/kWh)', 'Standing Charge (p/day)', 'Estimated Monthly Cost (£)', 'Estimated Yearly Cost (£)']
        ).format({
            'Day Rate (p/kWh)': '{:.2f}p',
            'Night Rate (p/kWh)': '{:.2f}p',
            'Standing Charge (p/day)': '{:.2f}p',
            'Estimated Monthly Cost (£)': '£{:.2f}',
            'Estimated Yearly Cost (£)': '£{:.2f}'
        })
        st.dataframe(styled_df, use_container_width=True)
    except ImportError:
        st.warning("`matplotlib` not installed. Cannot apply color formatting.")
        st.info("To enable colors, add `matplotlib` to your `requirements.txt` file.")
        # Display the unformatted dataframe as a fallback
        st.dataframe(final_comparison_df.style.format({
            'Day Rate (p/kWh)': '{:.2f}p',
            'Night Rate (p/kWh)': '{:.2f}p',
            'Standing Charge (p/day)': '{:.2f}p',
            'Estimated Monthly Cost (£)': '£{:.2f}',
            'Estimated Yearly Cost (£)': '£{:.2f}'
        }), use_container_width=True)
    except Exception as e:
        st.error(f"An unexpected error occurred while styling the table: {e}")
        st.dataframe(final_comparison_df, use_container_width=True) # Display raw data on other errors
