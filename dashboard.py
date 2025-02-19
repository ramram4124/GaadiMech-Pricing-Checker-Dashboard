import streamlit as st
import pandas as pd

# Set page configuration and custom CSS
st.set_page_config(
    page_title="GaadiMech Pricing Dashboard",
    page_icon="🔧",
    layout="wide"
)

# Custom CSS for GaadiMech branding
st.markdown("""
    <style>
        /* Main theme colors */
        :root {
            --gm-orange: #ff7200;
        }
        
        /* Header styling */
        .stTitle {
            color: var(--gm-orange) !important;
        }
        
        /* Metric containers */
        div[data-testid="stMetricValue"] {
            color: var(--gm-orange) !important;
            font-size: 24px !important;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #1E1E1E;
        }
        
        /* Cards for metrics */
        .metric-card {
            background-color: #1E1E1E;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid var(--gm-orange);
            margin: 10px 0;
        }
        
        /* Section headers */
        .section-header {
            color: var(--gm-orange);
            font-size: 24px;
            font-weight: bold;
            margin: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Load the cleaned dataset
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_dataset.csv')
    return df

# Remove the incorrect decorator and modify the initialization function
def initialize_session_state():
    if 'recent_searches' not in st.session_state:
        st.session_state.recent_searches = []
    if 'filters_changed' not in st.session_state:
        st.session_state.filters_changed = False

def add_to_recent_searches(car, fuel_type, service):
    # Create a search entry
    search_entry = {
        'timestamp': pd.Timestamp.now(),
        'car': car,
        'fuel_type': fuel_type,
        'service': service
    }
    
    # Add to recent searches and keep only last 5
    st.session_state.recent_searches.insert(0, search_entry)
    st.session_state.recent_searches = st.session_state.recent_searches[:5]

# Main function to run the dashboard
def main():
    # Header with logo colors
    st.markdown("""
        <h1 style='color: #ff7200;'>
            🔧 GaadiMech Service Price Dashboard
        </h1>
    """, unsafe_allow_html=True)
    
    # Subheader with custom styling
    st.markdown("""
        <p style='color: white; font-size: 20px; margin-bottom: 30px;'>
            Real-time Operations Monitoring
        </p>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Initialize session state (moved inside main)
    initialize_session_state()
    
    # Track if filters have changed from default
    def on_filter_change():
        st.session_state.filters_changed = True
    
    # Sidebar with custom styling
    st.sidebar.markdown("""
        <div style='background-color: #ff7200; padding: 10px; border-radius: 5px;'>
            <h2 style='color: white; margin: 0;'>Filters</h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Car Model filter
    car_models = ['All'] + sorted(df['car'].unique().tolist())
    selected_car = st.sidebar.selectbox("Select Car Model", car_models, on_change=on_filter_change)
    
    # Fuel Type filter
    if 'type' in df.columns:
        fuel_types = ['All'] + sorted(df['type'].unique().tolist())
    else:
        fuel_types = ['All']
    selected_fuel = st.sidebar.selectbox("Select Fuel Type", fuel_types, on_change=on_filter_change)
    
    # Service filter
    services = ['All'] + sorted(df['service'].astype(str).unique().tolist())
    selected_service = st.sidebar.selectbox("Select Service Type", services, on_change=on_filter_change)
    
    # Filter the dataframe based on selections
    filtered_df = df.copy()
    
    if selected_car != 'All':
        filtered_df = filtered_df[filtered_df['car'] == selected_car]
    if selected_fuel != 'All' and 'type' in filtered_df.columns:  # Changed to 'type'
        filtered_df = filtered_df[filtered_df['type'] == selected_fuel]
    if selected_service != 'All':
        filtered_df = filtered_df[filtered_df['service'] == selected_service]
    
    # Update recent searches if filters changed
    if st.session_state.filters_changed and not all(x == 'All' for x in [selected_car, selected_fuel, selected_service]):
        add_to_recent_searches(selected_car, selected_fuel, selected_service)
        st.session_state.filters_changed = False

    # Create container for better spacing
    with st.container():
        st.markdown("""
            <div class='section-header'>Service Price Overview</div>
        """, unsafe_allow_html=True)
        
        # Create grid layout for metrics
        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)
        
        # Function to get service prices for a specific service and selected car
        def get_service_prices(service_name, selected_car):
            service_df = df[df['service'] == service_name]
            if selected_car != 'All':
                service_df = service_df[service_df['car'] == selected_car]
            
            if len(service_df) > 0:
                if selected_car == 'All':
                    actual = service_df['actual price'].mean()
                    discounted = service_df['discounted price'].mean()
                else:
                    # Get the specific price for the selected car
                    actual = service_df['actual price'].iloc[0]
                    discounted = service_df['discounted price'].iloc[0]
                return f"₹{actual:,.2f} / ₹{discounted:,.2f}"
            return "No data"
        
        # Function to create styled metric card
        def metric_card(title, value, column):
            with column:
                st.markdown(f"""
                    <div class='metric-card'>
                        <p style='color: white; margin-bottom: 10px;'>{title}</p>
                        <h3 style='color: #ff7200; margin: 0;'>{value}</h3>
                    </div>
                """, unsafe_allow_html=True)
        
        # Display service prices in styled cards
        metric_card("Basic Service (Actual/Discounted)", 
                   get_service_prices("Basic Service", selected_car), col1)
        metric_card("Standard Service (Actual/Discounted)", 
                   get_service_prices("Standard Service", selected_car), col2)
        metric_card("Comprehensive Service (Actual/Discounted)", 
                   get_service_prices("Comprehensive Service", selected_car), col3)
        metric_card("Bonnet Paint (Actual/Discounted)", 
                   get_service_prices("Bonnet Paint", selected_car), col4)
    
    # Service Details section
    if all(x == 'All' for x in [selected_car, selected_fuel, selected_service]):
        # Show recent searches table
        st.markdown("""
            <div class='section-header'>Recent Searches</div>
        """, unsafe_allow_html=True)
        
        if st.session_state.recent_searches:
            recent_df = pd.DataFrame(st.session_state.recent_searches)
            recent_df['timestamp'] = recent_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
            recent_df.columns = ['Timestamp', 'Car Model', 'Fuel Type', 'Service']
            st.dataframe(
                recent_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No recent searches yet. Use the filters to search for services.")
    else:
        # Show Service Details table
        st.markdown("""
            <div class='section-header'>Service Details</div>
        """, unsafe_allow_html=True)
        
        # Style the dataframe
        st.markdown("""
            <style>
                .dataframe {
                    border: 1px solid #ff7200 !important;
                }
                .dataframe th {
                    background-color: #ff7200 !important;
                    color: white !important;
                }
                .dataframe td {
                    color: white !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Display service details table
        st.subheader("Service Details")
        
        # Create a more presentable view of the data
        display_columns = ['car', 'service category', 'actual price', 'discounted price', 'time taken', 'Warranty', 'Interval', 'Condition']
        
        if 'type' in filtered_df.columns:  # Changed to 'type'
            display_columns.insert(1, 'type')
        
        display_df = filtered_df[display_columns].copy()
        
        # Update column names
        if 'type' in display_df.columns:  # Changed to 'type'
            new_columns = [
                'Car Model',
                'Fuel Type',
                'Service Category',
                'Actual Price',
                'Discounted Price',
                'Service Time',
                'Warranty',
                'Service Interval',
                'Condition'
            ]
        else:
            new_columns = [
                'Car Model',
                'Service Category',
                'Actual Price',
                'Discounted Price',
                'Service Time',
                'Warranty',
                'Service Interval',
                'Condition'
            ]
        
        # Rename columns for better presentation
        display_df.columns = new_columns
        
        # Display the dataframe
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

if __name__ == "__main__":
    main() 
