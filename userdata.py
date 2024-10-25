import streamlit as st
from datetime import datetime
import json
import yfinance as yf
import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from pandas_datareader import data as pdr
import numpy as np


# Load user data from a JSON file
def load_user_data():
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


# Load existing users from the JSON file
users = load_user_data()

# Function to check user access and calculate remaining days based on permissions
def check_user_access(username):
    user_data = users.get(username, {})
    access_status = {}

    if user_data:
        # Check expiry date
        expiry_date = datetime.strptime(user_data['expiry_date'], '%Y-%m-%d')
        if datetime.now() > expiry_date:
            return {}  # Return empty dictionary if access has expired
        
        # Check permissions for dashboards
        permitted_dashboards = user_data.get('permissions', [])
        for dashboard in ['dashboard1', 'dashboard2', 'dashboard3', 'dashboard4', 'dashboard5', 'dashboard6']:
            if dashboard in permitted_dashboards:
                # Calculate remaining days
                days_left = (expiry_date - datetime.now()).days
                access_status[dashboard] = days_left
            else:
                # If not permitted, mark as no access
                access_status[dashboard] = "No access"
    
    return access_status

# Display user access information with professional styling
def display_user_access():
    if 'username' in st.session_state:
        access_status = check_user_access(st.session_state['username'])
        
        st.markdown("<h3 style='text-align: center;'>📊 Dashboard Access Information</h3>", unsafe_allow_html=True)
        st.markdown("<div style='display: flex; flex-wrap: wrap; justify-content: center;'>", unsafe_allow_html=True)
        
        # Loop through all dashboards
        for i in range(1, 7):
            dashboard_name = f'dashboard{i}'
            if dashboard_name in access_status:
                # Check if access is granted or denied
                if access_status[dashboard_name] == "No access":
                    # Display access denied with red and dark colors
                    card_html = f"""
                    <div style='background-color: #4a1414; color: #e74c3c; padding: 20px;
                        margin: 10px; border-radius: 12px; box-shadow: 4px 4px 20px rgba(0, 0, 0, 0.4);
                        text-align: center; width: 300px;' >
                        <h4>Dashboard {i}</h4>
                        <p>🔒 Access not granted</p>
                    </div>
                    """
                else:
                    # Display access granted with purple and blue colors
                    card_html = f"""
                    <div style='background-color: #2e2b5f; color: #2ecc71; padding: 20px;
                        margin: 10px; border-radius: 12px; box-shadow: 4px 4px 20px rgba(0, 0, 0, 0.4);
                        text-align: center; width: 300px;' >
                        <h4>Dashboard {i}</h4>
                        <p>✔️ Access granted</p>
                        <p>Expires in {access_status[dashboard_name]} days</p>
                    </div>
                    """
            else:
                # Handle case where access is not granted at all (fallback)
                card_html = f"""
                <div style='background-color: #4a1414; color: #e74c3c; padding: 20px;
                    margin: 10px; border-radius: 12px; box-shadow: 4px 4px 20px rgba(0, 0, 0, 0.4);
                    text-align: center; width: 300px;' >
                    <h4>Dashboard {i}</h4>
                    <p>🔒 Access not granted</p>
                </div>
                """
            
            st.markdown(card_html, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.write("Please log in to see your dashboard access status.")


# Function to fetch the Nifty 50 current price and show a message based on market condition
def fetch_nifty50_and_market_condition():
    ticker = yf.Ticker('^NSEI')  # Nifty 50 Index
    nifty_data = ticker.history(period='2d')  # Fetch 2 days of data to get the previous close

    if not nifty_data.empty and len(nifty_data) >= 2:
        current_price = nifty_data['Close'][-1]  # Get the latest close price
        previous_close = nifty_data['Close'][-2]  # Get the previous day's close price
        price_change_percentage = ((current_price - previous_close) / previous_close) * 100

        # Display appropriate message based on market condition
        if price_change_percentage < -0.5:
            st.warning("📉 Market gir gya hai! Time to invest with Whalestreet and make money!")
        elif price_change_percentage > 0.5:
            st.success("📈 Capitalize your gains! The market is going up!")
        else:
            st.info("🔄 The market is relatively stable. Keep an eye on opportunities.")
        
        return current_price, price_change_percentage
    else:
        st.error("Could not fetch enough Nifty 50 data.")
        return None, None

def main_dashboard():
    username = st.session_state.get('username', 'User')
    login_time = st.session_state.get('login_time', time.strftime("%Y-%m-%d %H:%M:%S"))

    if 'username' not in st.session_state or not st.session_state['username']:
        st.warning("Please log in to access your dashboards.")
        return

    # Add dark mode toggle
    dark_mode = st.checkbox("🌙 Dark Mode", False)
    
    if dark_mode:
        theme_color = "#1c1c1c"
        text_color = "#f1f1f1"
        card_bg = "#292929"
        button_bg = "#1abc9c"
        button_hover = "#16a085"
    else:
        theme_color = "#f7f8fa"
        text_color = "#2d3436"
        card_bg = "#ffffff"
        button_bg = "#2980b9"
        button_hover = "#3498db"

    # Styling and animations
    st.markdown(f"""
        <style>
            body, div, p, h1, h2, h3, h4, h5 {{
                font-family: 'Poppins', sans-serif;
                color: {text_color};
            }}
            .whalestreet-header {{
                background-color: {theme_color};
                color: {text_color};
                padding: 25px;
                text-align: center;
                border-radius: 10px;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.4);
            }}
            .dashboard-card {{
                background: {card_bg};
                padding: 30px;
                border-radius: 15px;
                box-shadow: 5px 5px 20px rgba(0, 0, 0, 0.4);
                text-align: center;
                max-width: 320px;
                transition: all 0.3s ease-in-out;
                position: relative;
                overflow: hidden;
                border: 1px solid #e1e1e1;
            }}
            .dashboard-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0px 8px 25px rgba(0, 0, 0, 0.5);
            }}
            .dashboard-button {{
                background-color: {button_bg};
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }}
            .dashboard-button:hover {{
                background-color: {button_hover};
            }}
            .stock-ticker {{
                background-color: {theme_color};
                padding: 10px;
                font-size: 18px;
                color: #2ecc71;
                display: flex;
                justify-content: center;
                align-items: center;
                white-space: nowrap;
                width: 100%;
                overflow: hidden;
                margin-bottom: 10px;
                position: relative;
            }}
            .ticker-text {{
                display: inline-block;
                animation: ticker 40s linear infinite;
            }}
            .stock-ticker:hover .ticker-text {{
                animation-play-state: paused;
            }}
            @keyframes ticker {{
                0% {{ transform: translateX(100%); }}
                100% {{ transform: translateX(-100%); }}
            }}
        </style>
    """, unsafe_allow_html=True)

    # Introduction Section
    st.markdown(f"""
        <div class="whalestreet-header">
            <h1>Welcome to Whalestreet Dashboard</h1>
            <p>Your gateway to stock market insights and powerful analytics.</p>
            <p>Explore a wide range of dashboards that provide real-time data and financial insights.</p>
        </div>
    """, unsafe_allow_html=True)

    # Fetch Nifty 50 stock data and show market condition
    current_price, price_change_percentage = fetch_nifty50_and_market_condition()

    st.write("---")

    # User greeting and login time
    st.markdown(f"""
        <div class="whalestreet-header">
            <h1>Hello, {username}!</h1>
            <p>You logged in at {login_time}</p>
        </div>
    """, unsafe_allow_html=True)

    # Interactive Help Button
    st.markdown(f"""
        <button class="help-btn" onclick="alert('Welcome to Whalestreet Dashboard! Navigate through your personalized dashboards and explore advanced analytics.')">?</button>
    """, unsafe_allow_html=True)

    # FAQ/Support Section (Collapsible)
    with st.expander("FAQs and Support"):
        st.write("**Q1: How do I access a dashboard?**")
        st.write("To access a dashboard, click on the 'Explore' button. If access is denied, please contact support.")
        st.write("**Q2: Can I customize my dashboard?**")
        st.write("Customization options are currently limited to admin users. Contact admin for further queries.")
        st.write("**Q3: How do I log out?**")
        st.write("There is no logout option, your session will expire automatically.")

    # Footer with social links
    st.markdown("""
        <div style="text-align:center; margin-top: 20px;">
            <p>&copy; 2024 Whalestreet. All Rights Reserved.</p>
            <p>Follow us on
                <a href="https://twitter.com/whalestreet" target="_blank">Twitter</a>,
                <a href="https://linkedin.com/company/whalestreet" target="_blank">LinkedIn</a>
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Access control should dynamically come from your logic
    access_status = check_user_access(st.session_state['username'])
    
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    def create_dashboard_card(col, dashboard_number, access_key, icon, title, description):
        if access_status.get(access_key) == "No access":
            with col:
                st.markdown(f"""
                    <div class='dashboard-card dashboard-card-no-access'>
                        <span class='dashboard-icon'>{icon}</span>
                        <h3>{title}</h3>
                        <p>{description}</p>
                        <p>🔒 Access Denied</p>
                    </div>
                """, unsafe_allow_html=True)
                st.button(f"Explore {title}", disabled=True, key=f"dashboard_{dashboard_number}_button", help="You do not have access to this dashboard.")
        else:
            days_left = access_status.get(access_key, 0)
            progress_percent = (days_left / 30) * 100
            with col:
                st.markdown(f"""
                    <div class='dashboard-card dashboard-card-access'>
                        <span class='dashboard-icon'>{icon}</span>
                        <h3>{title}</h3>
                        <p>{description}</p>
                        <p>✔️ Access Granted</p>
                        <p>Expires in {days_left} days</p>
                        <div class="progress-bar">
                            <div class="progress" style="width: {progress_percent}%; background-color: #27ae60;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Explore {title}", key=f"dashboard_{dashboard_number}_button"):
                    st.session_state['page'] = f'dashboard{dashboard_number}'

    # First row of dashboards
    create_dashboard_card(col1, 1, 'dashboard1', '📊', 'Dashboard 1', 'Powerful stock market insights await.')
    create_dashboard_card(col2, 2, 'dashboard2', '📈', 'Dashboard 2', 'Deep dive into financial analytics.')
    create_dashboard_card(col3, 3, 'dashboard3', '📉', 'Dashboard 3', 'Analyze trends and predict outcomes.')

    # Second row of dashboards
    create_dashboard_card(col4, 4, 'dashboard4', '📅', 'Dashboard 4', 'Track performance over time.')
    create_dashboard_card(col5, 5, 'dashboard5', '🔍', 'Dashboard 5', 'Custom searches and insights at your fingertips.')
    create_dashboard_card(col6, 6, 'dashboard6', '🧮', 'Dashboard 6', 'Advanced calculations and analytics.')


# Blank dashboard placeholders with back button and navigation to other dashboards based on granted permissions
def dashboard1():
    st.title("Dashboard 1")

    # Override Yahoo Finance restrictions
    yf.pdr_override()

    # Define the list of Nifty 50 top 5 stock symbols (you can update this list)
    stocks = {
        'TCS': 'TCS.NS',
        'Infosys': 'INFY.NS',
        'Reliance': 'RELIANCE.NS',
        'HDFC Bank': 'HDFCBANK.NS',
        'ICICI Bank': 'ICICIBANK.NS'
    }

    # Function to download stock data
    @st.cache
    def download_stock_data(stock_symbol):
        data = pdr.get_data_yahoo(stock_symbol, start="2000-01-01", end="2024-01-01")
        return data

    # Function to calculate monthly percentage change (based on 1st day opening and last day closing)
    def calculate_monthly_percentage_change(data):
        # Reset the index to work with dates
        data = data.reset_index()

        # Extract year and month from the Date column
        data['Year'] = data['Date'].dt.year
        data['Month'] = data['Date'].dt.month

        # Get the opening price of the first day of each month and the closing price of the last day of each month
        monthly_data = data.groupby(['Year', 'Month']).agg(
            Opening_Price=('Open', 'first'),
            Closing_Price=('Close', 'last')
        ).reset_index()

        # Calculate the monthly percentage change
        monthly_data['Pct Change'] = ((monthly_data['Closing_Price'] - monthly_data['Opening_Price']) / monthly_data['Opening_Price']) * 100

        # Pivot to get the heatmap structure (years as rows, months as columns)
        heatmap_data = monthly_data.pivot(index='Year', columns='Month', values='Pct Change')

        # Add a row for the average percentage change for each month across all years
        heatmap_data.loc['Average'] = heatmap_data.mean()

        # Convert month numbers to month names for better readability
        heatmap_data.columns = [pd.to_datetime(f'{m}', format='%m').strftime('%B') for m in heatmap_data.columns]

        return heatmap_data, monthly_data

    # Function to calculate the number of positive months and the ratio
    def calculate_positive_ratio(monthly_data):
        positive_count = monthly_data.groupby('Month')['Pct Change'].apply(lambda x: (x > 0).sum())  # Number of positive months
        total_count = monthly_data.groupby('Month')['Pct Change'].count()  # Total number of months
        ratio = (positive_count / total_count) * 100  # Positive ratio as a percentage

        # Convert month numbers to month names
        month_names = [pd.to_datetime(f'{m}', format='%m').strftime('%B') for m in total_count.index]

        # Create a dataframe to display
        ratio_data = pd.DataFrame({
            'Month': month_names,
            'Positive Months': positive_count.values,
            'Total Months': total_count.values,
            'Positive Ratio (%)': ratio.values
        }).set_index('Month')

        return ratio_data

    # Function to calculate yearly percentage change
    def calculate_yearly_percentage_change(data):
        # Ensure the 'Year' column is extracted from the Date column
        data = data.reset_index()
        data['Year'] = data['Date'].dt.year

        yearly_data = data.groupby('Year').agg(
            Opening_Price=('Open', 'first'),
            Closing_Price=('Close', 'last')
        ).reset_index()

        # Calculate the yearly percentage change
        yearly_data['Yearly Pct Change'] = ((yearly_data['Closing_Price'] - yearly_data['Opening_Price']) / yearly_data['Opening_Price']) * 100

        return yearly_data[['Year', 'Yearly Pct Change']].set_index('Year')

    # Streamlit App Layout
    st.title("Nifty 50 Top 5 Stocks - Monthly and Yearly Performance Heatmap")
    st.write("Select a stock from the dropdown below to view its historical performance based on the opening price of the first day of each month and the closing price of the last day of the month.")

    # Dropdown menu to select a stock
    selected_stock = st.selectbox("Select Stock", list(stocks.keys()))

    # Get the selected stock symbol
    stock_symbol = stocks[selected_stock]

    # Download stock data for the selected stock
    stock_data = download_stock_data(stock_symbol)

    # Calculate monthly percentage change
    monthly_returns, monthly_data = calculate_monthly_percentage_change(stock_data)

    # Calculate the positive-to-total ratio
    positive_ratio_data = calculate_positive_ratio(monthly_data)

    # Calculate yearly percentage change
    yearly_returns = calculate_yearly_percentage_change(stock_data)

    # Add the yearly percentage change as a new column to the heatmap
    monthly_returns['Yearly Change'] = yearly_returns['Yearly Pct Change']

    # Display the heatmap with custom colormap for positive and negative values
    st.subheader(f"Monthly and Yearly Percentage Change for {selected_stock} (2000 to 2024)")

    fig, ax = plt.subplots(figsize=(12, 8))

    # Use a TwoSlopeNorm to handle separate color mapping for positive and negative values
    norm = TwoSlopeNorm(vmin=monthly_returns.min().min(), vcenter=0, vmax=monthly_returns.max().max())

    # Create a custom colormap for positive (green) and negative (red) values
    cmap = sns.color_palette("RdYlGn", as_cmap=True)

    # Plot the heatmap
    sns.heatmap(monthly_returns, cmap=cmap, norm=norm, annot=True, fmt=".1f", ax=ax, linewidths=0.5, cbar_kws={"label": "% Change"})

    # Improve the heatmap appearance
    ax.set_title(f"{selected_stock} Monthly Performance Heatmap (with Yearly % Change)", fontsize=16)
    ax.set_ylabel("Year", fontsize=12)
    ax.set_xlabel("Month", fontsize=12)
    st.pyplot(fig)

    # Display the positive months ratio data
    st.subheader(f"Positive-to-Total Ratio for {selected_stock}")
    st.write(positive_ratio_data)

    # Show the raw data (optional)
    if st.checkbox("Show raw data"):
        st.write(stock_data)

    navigate_back_and_between_dashboards()

def dashboard2():
    st.title("Dashboard 2")
    st.write("This is where you will add your dashboard logic for Dashboard 2.")
    navigate_back_and_between_dashboards()

def dashboard3():
    st.title("Dashboard 3")
    st.write("This is where you will add your dashboard logic for Dashboard 3.")
    navigate_back_and_between_dashboards()

def dashboard4():
    st.title("Dashboard 4")
    st.write("This is where you will add your dashboard logic for Dashboard 4.")
    navigate_back_and_between_dashboards()

def dashboard5():
    st.title("Dashboard 5")
    st.write("This is where you will add your dashboard logic for Dashboard 5.")
    navigate_back_and_between_dashboards()

def dashboard6():
    st.title("Dashboard 6")
    st.write("This is where you will add your dashboard logic for Dashboard 6.")
    navigate_back_and_between_dashboards()

# Back button and inter-dashboard navigation options based on permissions
def navigate_back_and_between_dashboards():
    # Get user access permissions
    access_status = check_user_access(st.session_state['username'])

    if st.button("Back to Main Menu"):
        st.session_state['page'] = 'main'
    
    st.write("---")
    st.write("Navigate to other dashboards you have access to:")

    # Show buttons for only the dashboards the user has access to
    if access_status.get('dashboard1') != "No access":
        if st.button("Go to Dashboard 1"):
            st.session_state['page'] = 'dashboard1'
    if access_status.get('dashboard2') != "No access":
        if st.button("Go to Dashboard 2"):
            st.session_state['page'] = 'dashboard2'
    if access_status.get('dashboard3') != "No access":
        if st.button("Go to Dashboard 3"):
            st.session_state['page'] = 'dashboard3'
    if access_status.get('dashboard4') != "No access":
        if st.button("Go to Dashboard 4"):
            st.session_state['page'] = 'dashboard4'
    if access_status.get('dashboard5') != "No access":
        if st.button("Go to Dashboard 5"):
            st.session_state['page'] = 'dashboard5'
    if access_status.get('dashboard6') != "No access":
        if st.button("Go to Dashboard 6"):
            st.session_state['page'] = 'dashboard6'

# Function to handle routing between pages based on session state
def handle_dashboard_navigation():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'main'

    # Conditional rendering of pages based on session state
    if st.session_state['page'] == 'dashboard1':
        dashboard1()
    elif st.session_state['page'] == 'dashboard2':
        dashboard2()
    elif st.session_state['page'] == 'dashboard3':
        dashboard3()
    elif st.session_state['page'] == 'dashboard4':
        dashboard4()
    elif st.session_state['page'] == 'dashboard5':
        dashboard5()
    elif st.session_state['page'] == 'dashboard6':
        dashboard6()
    else:
        main_dashboard()

# User login page
def user_login():
    st.title("Client Login")
    st.write("Please enter your username and password to access your dashboard.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Check if the username exists and the password matches
        if username in users and users[username]['password'] == password:
            # Check if the user's access has expired
            expiry_date = datetime.strptime(users[username]['expiry_date'], '%Y-%m-%d')
            if datetime.now() > expiry_date:
                st.error(f"Your access expired on {expiry_date.strftime('%Y-%m-%d')}. Please contact admin.")
            else:
                # Login successful, update session state
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
        else:
            st.error("Invalid username or password.")

# Function to handle session-based login and navigation
def handle_login_navigation():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        user_login()
    else:
        handle_dashboard_navigation()

# Run the user dashboard
if __name__ == "__main__":
    handle_login_navigation()
