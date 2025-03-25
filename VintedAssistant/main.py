import streamlit as st
import pandas as pd
import time
import os
from vinted_scraper import VintedScraper
from deal_analyzer import DealAnalyzer
from discord_notifier import DiscordNotifier
import hashlib
import random  # Import random for random selections

# ------------------------------
# USER AUTHENTICATION SYSTEM
# ------------------------------


# Fake user database (replace with a real database if needed)
USER_CREDENTIALS = {
    "admin": hashlib.sha256("password123".encode()).hexdigest(),
    "user1": hashlib.sha256("securepass".encode()).hexdigest(),
}

# Function to check login
def check_login(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return USER_CREDENTIALS.get(username) == hashed_password

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login Page
if not st.session_state.logged_in:
    st.title("🔑 Login to Vinted Deal Monitor")
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if check_login(username, password):
            st.session_state.logged_in = True
            st.success("✅ Login successful! Redirecting...")
            time.sleep(1)  # Pause before loading main content
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")

    st.stop()  # Stop execution if not logged in


# Constants
DEALS_CSV_PATH = "deals.csv"

# Page config
st.set_page_config(
    page_title="Vinted Deal Monitor",
    page_icon="🛍️",
    layout="wide"
)

# Initialize session state
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = False
if 'last_scan_time' not in st.session_state:
    st.session_state.last_scan_time = None
if 'total_scanned' not in st.session_state:
    st.session_state.total_scanned = 0
if 'previous_deals' not in st.session_state:
    st.session_state.previous_deals = []
if 'all_deals' not in st.session_state:
    st.session_state.all_deals = []

# Load past deals from CSV if exists
if os.path.exists(DEALS_CSV_PATH):
    st.session_state.all_deals = pd.read_csv(DEALS_CSV_PATH).to_dict(orient="records")

# Main title
st.title("🛍️ Vinted Deal Monitor")

# Sidebar configuration
st.sidebar.header("Settings")

# Discord Webhook URL
webhook_url = st.sidebar.text_input(
    "Discord Webhook URL",
    value="https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE",
    type="password"
)

# Filtering options
min_price = st.sidebar.number_input("Minimum Price (£)", value=0.0, step=1.0)
max_price = st.sidebar.number_input("Maximum Price (£)", value=1000.0, step=1.0)
profit_threshold = st.sidebar.number_input("Minimum Profit Threshold (£)", value=5.0, step=1.0)
scan_interval = st.sidebar.number_input("Scan Interval (seconds)", value=300, min_value=120, help="How often to check for new deals. Keep this high (5+ minutes) to avoid being blocked by Vinted.")

# Brand selection
brands = [
    "Nike", "Adidas", "Puma", "New Balance", "Jordan", "Reebok",
    "Supreme", "Palace", "Stussy", "BAPE", "Off-White", "Stone Island",
    "Carhartt", "The North Face", "Nike x Off-White", "Yeezy", "Fear of God",
    "Palm Angels", "Essentials", "Chrome Hearts", "Ralph Lauren",
    "Tommy Hilfiger", "Patagonia", "Arc'teryx", "Trapstar", "Corteiz", "Other"
]

# Allow user to choose "Any Brand" or select specific brands
any_brand_option = st.sidebar.checkbox("Use Any Brand Randomly", value=False)

if any_brand_option:
    selected_brands = [random.choice(brands)]  # Select one random brand
    st.sidebar.write(f"Monitoring random brand: {selected_brands[0]}")
else:
    selected_brands = st.sidebar.multiselect("Filter Brands", brands, default=["Nike", "Adidas", "Supreme"])

# Initialize components
scraper = VintedScraper()
analyzer = DealAnalyzer(profit_threshold)
notifier = DiscordNotifier(webhook_url)

# Start/Stop monitoring button
if st.sidebar.button("Toggle Monitoring"):
    st.session_state.monitoring = not st.session_state.monitoring
    if st.session_state.monitoring:
        st.session_state.last_scan_time = time.time()

# Main content area
if st.session_state.monitoring:
    st.success(f"🟢 Monitoring is active - checking for deals every {scan_interval} seconds")
else:
    st.error("🔴 Monitoring is stopped")

# Create columns for stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Items Scanned", st.session_state.total_scanned)
with col2:
    st.metric("Brands Monitored", len(selected_brands))
with col3:
    st.metric("Last Scan", "Never" if not st.session_state.last_scan_time else time.strftime("%H:%M:%S", time.localtime(st.session_state.last_scan_time)))
with col4:
    st.metric("Next Scan In", "N/A" if not st.session_state.monitoring else f"{max(0, scan_interval - (time.time() - st.session_state.last_scan_time)):.0f}s")

# Main monitoring loop
if st.session_state.monitoring:
    try:
        current_time = time.time()
        if not st.session_state.last_scan_time or (current_time - st.session_state.last_scan_time) >= scan_interval:
            with st.spinner("🔍 Scanning Vinted listings..."):
                all_listings = []

                # Show progress bar
                progress_bar = st.progress(0)
                progress_text = st.empty()

                for i in range(0, len(selected_brands), 4):
                    batch_brands = selected_brands[i:i+4]
                    batch_listings = scraper.get_listings(
                        min_price=min_price,
                        max_price=max_price,
                        brands=batch_brands
                    )
                    all_listings.extend(batch_listings)
                    time.sleep(0.2)

                    # Update progress
                    progress_bar.progress(min(1.0, (i+2) / len(selected_brands)))
                    progress_text.text(f"Searching for {', '.join(batch_brands)}...")

                # Clear progress indicators
                progress_bar.empty()
                progress_text.empty()

                # Update scan stats
                st.session_state.total_scanned += len(all_listings)
                st.session_state.last_scan_time = current_time

                # Track new deals
                seen_ids = set(deal.get('id', '') for deal in st.session_state.previous_deals)
                new_listings = [item for item in all_listings if item.get('id', '') not in seen_ids]

                if new_listings:
                    new_deals = analyzer.find_deals(new_listings)
                    if new_deals:
                        st.session_state.all_deals = new_deals + st.session_state.all_deals
                        st.session_state.all_deals = st.session_state.all_deals[:100]

                        for deal in new_deals:
                            notifier.send_deal(deal)

                        # Save deals to CSV
                        pd.DataFrame(st.session_state.all_deals).to_csv(DEALS_CSV_PATH, index=False)

                st.session_state.previous_deals = all_listings

            # Display all deals in a table
            if st.session_state.all_deals:
                st.success(f"🎯 Found {len(st.session_state.all_deals)} potential deals!")

                df = pd.DataFrame(st.session_state.all_deals[:30])  # Show top 30 deals
                st.dataframe(
                    df[['title', 'size', 'price', 'estimated_profit', 'profit_percentage', 'url']],  # Added 'size'
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        'size': st.column_config.TextColumn('Size'),
                        'price': st.column_config.NumberColumn('Price (£)', format="£%.2f"),
                        'estimated_profit': st.column_config.NumberColumn('Potential Profit (£)', format="£%.2f"),
                        'profit_percentage': st.column_config.NumberColumn('Profit %', format="%.1f%%"),
                        'url': st.column_config.LinkColumn('Link')
                    }
                )

            else:
                st.info("👀 No deals found yet - keeping watch!")

        # Add a small delay
        time.sleep(0.2)
        st.rerun()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        time.sleep(5)
        st.rerun()

# Display instructions
with st.expander("How to Use"):
    st.markdown("""
    1. Enter your Discord webhook URL in the sidebar.
    2. Configure your desired price range and profit threshold.
    3. Select brands to monitor, or choose to monitor any random brand.
    4. Click 'Toggle Monitoring' to start/stop the monitor.
    5. The app will scan Vinted every few seconds and notify you of good deals.
    6. Deals will appear in the table and be saved to CSV.
    """)






