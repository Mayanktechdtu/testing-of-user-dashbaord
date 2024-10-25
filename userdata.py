import streamlit as st
from datetime import datetime
import sqlite3
import yfinance as yf
import time

# Connect to the SQLite database (creates the file if it doesn’t exist)
conn = sqlite3.connect('clients.db')
cursor = conn.cursor()

# Create the clients table if it doesn’t exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        username TEXT PRIMARY KEY,
        password TEXT,
        expiry_date TEXT,
        permissions TEXT
    )
''')
conn.commit()

# Function to retrieve client data by username
def get_client(username):
    cursor.execute('SELECT * FROM clients WHERE username = ?', (username,))
    client = cursor.fetchone()
    if client:
        return {
            'username': client[0],
            'password': client[1],
            'expiry_date': client[2],
            'permissions': client[3].split(',')
        }
    return None

# Function to check user access and calculate remaining days based on permissions
def check_user_access(username):
    client_data = get_client(username)
    access_status = {}

    if client_data:
        expiry_date = datetime.strptime(client_data['expiry_date'], '%Y-%m-%d')
        if datetime.now() > expiry_date:
            return {}  # Return empty if access has expired
        
        # Check permissions for dashboards
        permitted_dashboards = client_data['permissions']
        for dashboard in ['dashboard1', 'dashboard2', 'dashboard3', 'dashboard4', 'dashboard5', 'dashboard6']:
            if dashboard in permitted_dashboards:
                days_left = (expiry_date - datetime.now()).days
                access_status[dashboard] = days_left
            else:
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
                if access_status[dashboard_name] == "No access":
                    # Access denied card
                    card_html = f"""
                    <div style='background-color: #4a1414; color: #e74c3c; padding: 20px;
                        margin: 10px; border-radius: 12px; box-shadow: 4px 4px 20px rgba(0, 0, 0, 0.4);
                        text-align: center; width: 300px;' >
                        <h4>Dashboard {i}</h4>
                        <p>🔒 Access not granted</p>
                    </div>
                    """
                else:
                    # Access granted card
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

# Fetch the Nifty 50 current price and show a message based on market condition
def fetch_nifty50_and_market_condition():
    ticker = yf.Ticker('^NSEI')  # Nifty 50 Index
    nifty_data = ticker.history(period='2d')  # Fetch 2 days of data to get the previous close

    if not nifty_data.empty and len(nifty_data) >= 2:
        current_price = nifty_data['Close'][-1]
        previous_close = nifty_data['Close'][-2]
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
    st.write("This is where you will add your dashboard logic for Dashboard 1.")
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
    access_status = check_user_access(st.session_state['username'])

    if st.button("Back to Main Menu"):
        st.session_state['page'] = 'main'
    
    st.write("---")
    st.write("Navigate to other dashboards you have access to:")

    for i in range(1, 7):
        dashboard_name = f'dashboard{i}'
        if access_status.get(dashboard_name) != "No access":
            if st.button(f"Go to Dashboard {i}"):
                st.session_state['page'] = dashboard_name

# Handle routing between pages based on session state
def handle_dashboard_navigation():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'main'

    # Conditional rendering of pages
    if st.session_state['page'] == 'dashboard1':
        dashboard1()
    # Add more conditions for other dashboards
    else:
        main_dashboard()

# User login page
def user_login():
    st.title("Client Login")
    st.write("Please enter your username and password to access your dashboard.")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        client_data = get_client(username)
        if client_data and client_data['password'] == password:
            expiry_date = datetime.strptime(client_data['expiry_date'], '%Y-%m-%d')
            if datetime.now() > expiry_date:
                st.error(f"Your access expired on {expiry_date.strftime('%Y-%m-%d')}. Please contact admin.")
            else:
                # Login successful
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['login_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            st.error("Invalid username or password.")

# Handle login and navigation
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
