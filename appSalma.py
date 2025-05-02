#idV	modele	marque	annee	puissance	type	prixAchat	prixVente	stockShowroom	stockParc
#stockShowroom	stockParc
import streamlit as st
import pandas as pd
import os
import hashlib
import uuid
import time
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime
import re
from PIL import Image

# Set page configuration
st.set_page_config(
    page_title="Prestige Motors Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Data file paths
BASE_DIR = os.path.dirname(__file__)
INVENTORY_PATH = os.path.join(BASE_DIR, 'data', 'inventory.csv')
USERS_PATH = os.path.join(BASE_DIR, 'data', 'users.csv')
LOGS_PATH = os.path.join(BASE_DIR, 'data', 'activity_logs.csv')

# Ensure all required data directories and files exist
def initialize_data_files():
    os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
    
    # Initialize inventory file if it doesn't exist
    if not os.path.exists(INVENTORY_PATH):
        pd.DataFrame({
            'id': [],
            'make': [],
            'model': [],
            'year': [],
            'price': [],
            'status': [],
            'location': [],
            'date_added': [],
            'last_updated': []
        }).to_csv(INVENTORY_PATH, index=False)
    
    # Initialize users file if it doesn't exist
    if not os.path.exists(USERS_PATH):
        # Create default admin user with hashed password
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        pd.DataFrame({
            'username': ['admin'],
            'password_hash': [admin_password],
            'role': ['admin'],
            'last_login': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }).to_csv(USERS_PATH, index=False)
    
    # Initialize logs file if it doesn't exist
    if not os.path.exists(LOGS_PATH):
        pd.DataFrame({
            'timestamp': [],
            'user': [],
            'action': [],
            'details': []
        }).to_csv(LOGS_PATH, index=False)

# Load CSS
def load_css():
    with open(os.path.join(BASE_DIR, 'styles.css'), 'r') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Data loading with caching
@st.cache_data(ttl=300)
def load_inventory():
    """Load inventory data with caching for 5 minutes"""
    try:
        return pd.read_csv(INVENTORY_PATH)
    except Exception as e:
        st.error(f"Error loading inventory data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_users():
    """Load users data with caching for 5 minutes"""
    try:
        return pd.read_csv(USERS_PATH)
    except Exception as e:
        st.error(f"Error loading users data: {e}")
        return pd.DataFrame()

# CRUD Operations
def save_inventory(df):
    """Save inventory data to CSV"""
    with st.spinner("Saving data..."):
        try:
            df.to_csv(INVENTORY_PATH, index=False)
            log_activity(st.session_state.get('username', 'system'), "update_inventory", "Inventory data updated")
            return True
        except Exception as e:
            st.error(f"Error saving inventory data: {e}")
            return False

def add_car_to_inventory(make, model, year, price, status, location):
    """Add a new car to inventory"""
    inventory = load_inventory()
    
    # Generate unique ID
    new_id = str(uuid.uuid4())[:8]
    if 'id' in inventory.columns and not inventory.empty:
        while new_id in inventory['id'].values:
            new_id = str(uuid.uuid4())[:8]
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_car = pd.DataFrame({
        'id': [new_id],
        'make': [make],
        'model': [model],
        'year': [year],
        'price': [price],
        'status': [status],
        'location': [location],
        'date_added': [now],
        'last_updated': [now]
    })
    
    updated_inventory = pd.concat([inventory, new_car], ignore_index=True)
    if save_inventory(updated_inventory):
        log_activity(st.session_state.get('username', 'system'), "add_car", f"Added {make} {model} to inventory")
        return True, new_id
    return False, None

def update_car(car_id, **kwargs):
    """Update car details"""
    inventory = load_inventory()
    
    if 'id' not in inventory.columns or car_id not in inventory['id'].values:
        return False, "Car not found in inventory"
    
    # Update only provided fields
    for field, value in kwargs.items():
        if field in inventory.columns:
            inventory.loc[inventory['id'] == car_id, field] = value
    
    # Update last_updated timestamp
    inventory.loc[inventory['id'] == car_id, 'last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if save_inventory(inventory):
        log_activity(st.session_state.get('username', 'system'), "update_car", f"Updated car {car_id}")
        return True, "Car updated successfully"
    return False, "Failed to update car"

def remove_car(car_id):
    """Remove a car from inventory"""
    inventory = load_inventory()
    
    if 'id' not in inventory.columns or car_id not in inventory['id'].values:
        return False, "Car not found in inventory"
    
    # Get car details for logging
    car_details = inventory[inventory['id'] == car_id].iloc[0]
    
    # Remove the car
    updated_inventory = inventory[inventory['id'] != car_id]
    
    if save_inventory(updated_inventory):
        log_activity(st.session_state.get('username', 'system'), "remove_car", 
                    f"Removed {car_details['make']} {car_details['model']} from inventory")
        return True, "Car removed successfully"
    return False, "Failed to remove car"

def log_activity(username, action, details):
    """Log user activity"""
    try:
        logs = pd.read_csv(LOGS_PATH)
        new_log = pd.DataFrame({
            'timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            'user': [username],
            'action': [action],
            'details': [details]
        })
        updated_logs = pd.concat([logs, new_log], ignore_index=True)
        updated_logs.to_csv(LOGS_PATH, index=False)
    except Exception as e:
        st.error(f"Error logging activity: {e}")

# Authentication
def verify_password(username, password):
    """Verify user credentials"""
    users = load_users()
    
    if username not in users['username'].values:
        return False
    
    user_data = users[users['username'] == username].iloc[0]
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if password_hash == user_data['password_hash']:
        # Update last login
        users.loc[users['username'] == username, 'last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        users.to_csv(USERS_PATH, index=False)
        return True
    
    return False

def authenticate_user():
    """Handle user authentication"""
    st.sidebar.header("Login")
    
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type='password')
    
    login_placeholder = st.sidebar.empty()
    
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    
    if login_placeholder.button("Login", key="login_button"):
        if not username or not password:
            st.sidebar.error("Username and password are required")
            return
        
        with st.spinner("Authenticating..."):
            time.sleep(0.5)  # Add slight delay for UX
            if verify_password(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.login_attempts = 0
                log_activity(username, "login", "User logged in")
                st.sidebar.success("Logged in successfully!")
                st.experimental_rerun()
            else:
                st.session_state.login_attempts += 1
                st.sidebar.error(f"Invalid credentials. Attempts: {st.session_state.login_attempts}")
                if st.session_state.login_attempts >= 5:
                    st.sidebar.warning("Too many failed attempts. Please try again later.")
                    time.sleep(5)
                    st.session_state.login_attempts = 0
    
    if st.session_state.get('authenticated', False):
        st.sidebar.success(f"Logged in as {st.session_state.username}")
        if st.sidebar.button("Logout"):
            log_activity(st.session_state.username, "logout", "User logged out")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

# Data validation
def validate_make_model(value):
    """Validate make/model input"""
    if not value:
        return False, "This field is required"
    if not re.match(r'^[A-Za-z0-9\s\-]+$', value):
        return False, "Only letters, numbers, spaces, and hyphens are allowed"
    return True, ""

def validate_year(value):
    """Validate year input"""
    current_year = datetime.now().year
    if value < 1900 or value > current_year + 1:
        return False, f"Year must be between 1900 and {current_year + 1}"
    return True, ""

def validate_price(value):
    """Validate price input"""
    if value <= 0:
        return False, "Price must be greater than zero"
    return True, ""

# Dashboard
def dashboard(data):
    """Display dashboard with KPIs and charts"""
    st.title("Prestige Motors Dashboard")
    
    # Add timestamp and refresh button
    col1, col2 = st.columns([3, 1])
    col1.text(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if col2.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.experimental_rerun()
    
    # Create a more sophisticated dashboard with metrics and charts
    with st.container():
        st.subheader("Key Performance Indicators")
        
        # Calculate KPIs
        total_cars = len(data)
        in_stock_cars = len(data[data['status'] == 'in stock'])
        sold_cars = len(data[data['status'] == 'sold'])
        deliveries_in_progress = len(data[data['status'] == 'in delivery'])
        showroom_cars = len(data[data['location'] == 'showroom']) if 'location' in data.columns else 0
        park_cars = len(data[data['location'] == 'park']) if 'location' in data.columns else 0
        total_capacity = 100  # Example capacity
        capacity_used = (total_cars / total_capacity) * 100
        
        # Display KPIs in a grid
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Cars in Stock", in_stock_cars, help="Total number of cars available for sale")
        col2.metric("Cars Sold", sold_cars, help="Total number of cars sold")
        col3.metric("Deliveries in Progress", deliveries_in_progress, help="Cars being delivered to customers")
        col4.metric("Capacity Utilization", f"{capacity_used:.1f}%", help="Percentage of total capacity used")
        
        # Second row of metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Showroom Cars", showroom_cars, help="Cars currently in the showroom")
        col2.metric("Park Cars", park_cars, help="Cars currently in the parking lot")
        col3.metric("Total Inventory", total_cars, help="Total number of cars in the system")
        col4.metric("Available Capacity", total_capacity - total_cars, help="Remaining capacity")
    
    # Charts section
    st.subheader("Inventory Insights")
    
    tab1, tab2, tab3 = st.tabs(["Status Distribution", "Price Distribution", "Brand Distribution"])
    
    with tab1:
        # Status distribution pie chart
        if not data.empty and 'status' in data.columns:
            status_counts = data['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            
            fig = px.pie(status_counts, values='Count', names='Status', 
                         title='Inventory Status Distribution',
                         color_discrete_sequence=px.colors.sequential.Viridis)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No status data available")
    
    with tab2:
        # Price distribution histogram
        if not data.empty and 'price' in data.columns:
            fig = px.histogram(data, x='price', nbins=20, 
                               title='Price Distribution',
                               labels={'price': 'Price ($)', 'count': 'Number of Cars'},
                               color_discrete_sequence=['#4c68c0'])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No price data available")
    
    with tab3:
        # Brand distribution bar chart
        if not data.empty and 'make' in data.columns:
            make_counts = data['make'].value_counts().reset_index()
            make_counts.columns = ['Make', 'Count']
            
            fig = px.bar(make_counts, x='Make', y='Count', 
                         title='Brand Distribution',
                         color='Count',
                         color_continuous_scale=px.colors.sequential.Viridis)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No make data available")
    
    # Recent activity log
    try:
        logs = pd.read_csv(LOGS_PATH).tail(5)
        
        st.subheader("Recent Activity")
        st.dataframe(logs, use_container_width=True)
    except:
        st.info("No activity logs available")

# Inventory tab
def inventory_tab(data):
    """Display and manage inventory"""
    st.title("Inventory Management")
    
    # Add search, filter, and sort options
    st.subheader("Search and Filter")
    
    col1, col2, col3 = st.columns(3)
    
    # Search functionality
    search_term = col1.text_input("Search by Make or Model")
    
    # Filter by status
    statuses = ['All'] + sorted(data['status'].unique().tolist())
    selected_status = col2.selectbox("Filter by Status", statuses)
    
    # Filter by price range
    min_price, max_price = int(data['price'].min()), int(data['price'].max())
    price_range = col3.slider("Price Range", min_price, max_price, (min_price, max_price))
    
    # Apply filters
    filtered_data = data.copy()
    
    if search_term:
        filtered_data = filtered_data[
            filtered_data['make'].str.contains(search_term, case=False) | 
            filtered_data['model'].str.contains(search_term, case=False)
        ]
    
    if selected_status != 'All':
        filtered_data = filtered_data[filtered_data['status'] == selected_status]
    
    filtered_data = filtered_data[
        (filtered_data['price'] >= price_range[0]) & 
        (filtered_data['price'] <= price_range[1])
    ]
    
    # Sort functionality
    sort_col, sort_direction = st.columns(2)
    sort_by = sort_col.selectbox("Sort by", ['make', 'model', 'year', 'price', 'status'])
    ascending = sort_direction.checkbox("Ascending order", True)
    
    filtered_data = filtered_data.sort_values(by=sort_by, ascending=ascending)
    
    # Display inventory with visual indicators
    if not filtered_data.empty:
        # Function to style rows based on status
        def style_status(row):
            if row['status'] == 'in stock':
                return f"background-color: rgba(76, 104, 192, 0.1); color: #2a2e70;"
            elif row['status'] == 'sold':
                return f"background-color: rgba(42, 46, 112, 0.1); color: #555269;"
            elif row['status'] == 'in delivery':
                return f"background-color: rgba(213, 209, 222, 0.3); color: #4c68c0;"
            return ""
        
        # Create stylable dataframe
        styled_df = filtered_data.style.apply(lambda row: [style_status(row) for _ in range(len(row))], axis=1)
        
        st.dataframe(styled_df, use_container_width=True, 
                  height=400)
        
        st.text(f"Showing {len(filtered_data)} of {len(data)} vehicles")
    else:
        st.info("No vehicles match your search criteria")
    
    # Action selection
    st.subheader("Actions")
    action = st.selectbox("Choose an action", ["Add Car", "Update Car", "Remove Car", "Move Car", "Estimate Price"])
    
    # Display appropriate form based on action
    if action == "Add Car":
        add_car_form()
    elif action == "Update Car":
        update_car_form(data)
    elif action == "Remove Car":
        remove_car_form(data)
    elif action == "Move Car":
        move_car_form(data)
    elif action == "Estimate Price":
        estimate_price_form(data)

# Action forms
def add_car_form():
    """Form to add a new car to inventory"""
    with st.form("add_car_form"):
        st.subheader("Add New Car")
        
        col1, col2 = st.columns(2)
        
        # Input fields with validation
        make = col1.text_input("Make")
        model = col1.text_input("Model")
        year = col1.number_input("Year", min_value=1900, max_value=datetime.now().year + 1, value=datetime.now().year)
        price = col2.number_input("Price ($)", min_value=0.0, value=20000.0, step=1000.0)
        status = col2.selectbox("Status", ["in stock", "sold", "in delivery"])
        location = col2.selectbox("Location", ["showroom", "park"])
        
        submit = st.form_submit_button("Add Car")
        
        if submit:
            # Validate inputs
            make_valid, make_error = validate_make_model(make)
            model_valid, model_error = validate_make_model(model)
            year_valid, year_error = validate_year(year)
            price_valid, price_error = validate_price(price)
            
            # Display validation errors
            if not make_valid:
                st.error(f"Make: {make_error}")
            if not model_valid:
                st.error(f"Model: {model_error}")
            if not year_valid:
                st.error(f"Year: {year_error}")
            if not price_valid:
                st.error(f"Price: {price_error}")
                
            # If all inputs are valid, add the car
            if make_valid and model_valid and year_valid and price_valid:
                with st.spinner("Adding car to inventory..."):
                    success, car_id = add_car_to_inventory(make, model, year, price, status, location)
                    
                    if success:
                        st.success(f"Car added successfully! ID: {car_id}")
                        # Clear cache to refresh data
                        st.cache_data.clear()
                    else:
                        st.error("Failed to add car. Please try again.")

def update_car_form(data):
    """Form to update a car in inventory"""
    if 'id' not in data.columns or data.empty:
        st.warning("No cars available to update")
        return
    
    car_options = data[['id', 'make', 'model', 'year']].apply(
        lambda row: f"{row['id']} - {row['make']} {row['model']} ({row['year']})", axis=1
    ).tolist()
    
    selected_car = st.selectbox("Select Car to Update", car_options)
    car_id = selected_car.split(" - ")[0] if selected_car else None
    
    if car_id:
        car_data = data[data['id'] == car_id].iloc[0]
        
        with st.form("update_car_form"):
            st.subheader(f"Update {car_data['make']} {car_data['model']}")
            
            col1, col2 = st.columns(2)
            
            # Pre-populate form with current values
            make = col1.text_input("Make", value=car_data['make'])
            model = col1.text_input("Model", value=car_data['model'])
            year = col1.number_input("Year", min_value=1900, max_value=datetime.now().year + 1, value=int(car_data['year']))
            price = col2.number_input("Price ($)", min_value=0.0, value=float(car_data['price']), step=1000.0)
            status = col2.selectbox("Status", ["in stock", "sold", "in delivery"], index=["in stock", "sold", "in delivery"].index(car_data['status']) if car_data['status'] in ["in stock", "sold", "in delivery"] else 0)
            location = col2.selectbox("Location", ["showroom", "park"], index=["showroom", "park"].index(car_data['location']) if 'location' in car_data and car_data['location'] in ["showroom", "park"] else 0)
            
            submit = st.form_submit_button("Update Car")
            
            if submit:
                # Validate inputs
                make_valid, make_error = validate_make_model(make)
                model_valid, model_error = validate_make_model(model)
                year_valid, year_error = validate_year(year)
                price_valid, price_error = validate_price(price)
                
                # Display validation errors
                if not make_valid:
                    st.error(f"Make: {make_error}")
                if not model_valid:
                    st.error(f"Model: {model_error}")
                if not year_valid:
                    st.error(f"Year: {year_error}")
                if not price_valid:
                    st.error(f"Price: {price_error}")
                    
                # If all inputs are valid, update the car
                if make_valid and model_valid and year_valid and price_valid:
                    with st.spinner("Updating car information..."):
                        success, message = update_car(
                            car_id, 
                            make=make, 
                            model=model, 
                            year=year, 
                            price=price, 
                            status=status,
                            location=location
                        )
                        
                        if success:
                            st.success(message)
                            # Clear cache to refresh data
                            st.cache_data.clear()
                        else:
                            st.error(message)

def remove_car_form(data):
    """Form to remove a car from inventory with confirmation"""
    if 'id' not in data.columns or data.empty:
        st.warning("No cars available to remove")
        return
    
    car_options = data[['id', 'make', 'model', 'year']].apply(
        lambda row: f"{row['id']} - {row['make']} {row['model']} ({row['year']})", axis=1
    ).tolist()
    
    selected_car = st.selectbox("Select Car to Remove", car_options)
    car_id = selected_car.split(" - ")[0] if selected_car else None
    
    if car_id:
        car_data = data[data['id'] == car_id].iloc[0]
        
        # Display car details for confirmation
        st.subheader(f"Remove {car_data['make']} {car_data['model']}")
        
        col1, col2 = st.columns(2)
        col1.text(f"ID: {car_id}")
        col1.text(f"Make: {car_data['make']}")
        col1.text(f"Model: {car_data['model']}")
        col2.text(f"Year: {car_data['year']}")
        col2.text(f"Price: ${car_data['price']}")
        col2.text(f"Status: {car_data['status']}")
        
        # Confirmation dialog
        st.warning("⚠️ This action cannot be undone. Are you sure you want to remove this car from inventory?")
        
        col1, col2 = st.columns(2)
        confirm = col1.checkbox("I confirm I want to remove this car")
        
        if confirm:
            if col2.button("Remove Car"):
                with st.spinner("Removing car from inventory..."):
                    success, message = remove_car(car_id)
                    
                    if success:
                        st.success(message)
                        # Clear cache to refresh data
                        st.cache_data.clear()
                    else:
                        st.error(message)

def move_car_form(data):
    """Form to move a car to a different location"""
    if 'id' not in data.columns or data.empty:
        st.warning("No cars available to move")
        return
    
    # Filter to show only in-stock cars
    in_stock_data = data[data['status'] == 'in stock']
    
    if in_stock_data.empty:
        st.warning("No in-stock cars available to move")
        return
    
    car_options = in_stock_data[['id', 'make', 'model', 'year', 'location']].apply(
        lambda row: f"{row['id']} - {row['make']} {row['model']} ({row['year']}) - Currently: {row.get('location', 'N/A')}", axis=1
    ).tolist()
    
    selected_car = st.selectbox("Select Car to Move", car_options)
    car_id = selected_car.split(" - ")[0] if selected_car else None
    
    if car_id:
        car_data = data[data['id'] == car_id].iloc[0]
        current_location = car_data.get('location', 'unknown')
        
        st.subheader(f"Move {car_data['make']} {car_data['model']}")
        
        locations = ["showroom", "park"]
        if current_location in locations:
            locations.remove(current_location)
            default_new_location = locations[0]
        else:
            default_new_location = "showroom"
        
        new_location = st.selectbox(
            f"Move from {current_location} to:", 
            locations,
            index=0
        )
        
        if st.button(f"Move to {new_location.title()}"):
            with st.spinner(f"Moving car to {new_location}..."):
                success, message = update_car(car_id, location=new_location)
                
                if success:
                    st.success(f"Car moved to {new_location} successfully!")
                    # Clear cache to refresh data
                    st.cache_data.clear()
                else:
                    st.error(message)

def estimate_price_form(data):
    """Form to estimate price based on make, model, and year"""
    st.subheader("Estimate Car Price")
    
    col1, col2 = st.columns(2)
    
    make = col1.text_input("Make")
    model = col1.text_input("Model")
    year = col2.number_input("Year", min_value=1900, max_value=datetime.now().year + 1, value=datetime.now().year)
    mileage = col2.number_input("Mileage", min_value=0, value=10000)
    
    if st.button("Estimate Price"):
        if not make or not model:
            st.error("Make and model are required")
            return
        
        with st.spinner("Calculating estimate..."):
            # Simple price estimation algorithm
            # In a real application, this would be more sophisticated
            similar_cars = data[
                (data['make'].str.lower() == make.lower()) & 
                (data['model'].str.lower() == model.lower())
            ]
            
            if not similar_cars.empty:
                avg_price = similar_cars['price'].mean()
                price_range = (avg_price * 0.9, avg_price * 1.1)
                
                # Adjust for year difference
                year_adjustment = (year - similar_cars['year'].mean()) * 1000
                
                estimated_price = avg_price + year_adjustment
                
                # Adjust for mileage (simplified)
                estimated_price = estimated_price - (mileage / 10000) * 1000
                
                estimated_price = max(estimated_price, 1000)  # Minimum price
                
                st.success(f"Estimated Price: ${estimated_price:,.2f}")
                st.info(f"Price range: ${price_range[0]:,.2f} - ${price_range[1]:,.2f}")
            else:
                # Fallback for unknown make/model
                st.warning("No similar cars found for accurate estimation")
                
                # Base price by year
                base_price = (datetime.now().year - year) * 1000
                estimated_price = 20000 - base_price - (mileage / 10000) * 1000
                estimated_price = max(estimated_price, 1000)  # Minimum price
                
                st.info(f"Rough Estimate: ${estimated_price:,.2f}")
                st.text("This is a very rough estimate as we don't have similar cars in our database")

# Main function
def main():
    """Main application entry point"""
    # Initialize data files
    initialize_data_files()
    
    # Load CSS
    load_css()
    
    # Hide default Streamlit elements
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    authenticate_user()
    
    # Main application
    if st.session_state.get('authenticated', False):
        # Load data with spinner
        with st.spinner("Loading data..."):
            data = load_inventory()
        
        # Create tabs
        tabs = st.tabs(["Dashboard", "Inventory"])
        
        with tabs[0]:
            dashboard(data)
        
        with tabs[1]:
            inventory_tab(data)
    else:
        # Welcome page for non-authenticated users
        st.title("Welcome to Prestige Motors")
        st.subheader("Luxury Vehicle Management System")
        
        st.info("Please log in using the sidebar to access the system")
        
        # Display demo image or placeholder
        st.image("https://images.unsplash.com/photo-1511919884226-fd3cad34687c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80", 
                 caption="Luxury vehicles deserve premium management")

if __name__ == "__main__":
    main()