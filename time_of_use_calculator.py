import streamlit as st
from datetime import datetime
import holidays  # pip install holidays

def is_holiday(now):
    # Check U.S. holidays for the current year.
    us_holidays = holidays.US(years=now.year)
    return now.date() in us_holidays

def get_tou_bucket(now):
    """
    Determine the current TOU bucket for TOU-DR1 Residential.
    
    Weekdays (non-holidays):
      - 12:00 a.m. – 6:00 a.m.: Super Off-Peak
      - 6:00 a.m. – 4:00 p.m.: Off-Peak 
         (with extra off-peak from 10:00 a.m. – 2:00 p.m. in March/April)
      - 4:00 p.m. – 9:00 p.m.: On-Peak
      - 9:00 p.m. – 12:00 a.m.: Off-Peak
      
    Weekends and Holidays:
      - 12:00 a.m. – 2:00 p.m.: Super Off-Peak
      - 2:00 p.m. – 4:00 p.m.: Off-Peak
      - 4:00 p.m. – 9:00 p.m.: On-Peak
      - 9:00 p.m. – 12:00 a.m.: Off-Peak
    """
    t = now.hour + now.minute / 60.0  # current time in decimal hours

    # Use weekend logic if it's Saturday, Sunday, or a holiday.
    if now.weekday() >= 5 or is_holiday(now):
        if t < 14:  # 12:00 a.m. - 2:00 p.m.
            return "Super Off-Peak (Weekend/Holiday)"
        elif t < 16:  # 2:00 p.m. - 4:00 p.m.
            return "Off-Peak (Weekend/Holiday)"
        elif t < 21:  # 4:00 p.m. - 9:00 p.m.
            return "On-Peak (Weekend/Holiday)"
        else:  # 9:00 p.m. - 12:00 a.m.
            return "Off-Peak (Weekend/Holiday)"
    else:
        # Weekday logic
        if t < 6:
            return "Super Off-Peak (Weekday)"
        elif t < 16:  # 6:00 a.m. to 4:00 p.m.
            # Extra off-peak window in March/April: 10:00 a.m. to 2:00 p.m.
            if now.month in (3, 4) and 10 <= t < 14:
                return "Extra Off-Peak (Mar/Apr, Weekday)"
            else:
                return "Off-Peak (Weekday)"
        elif t < 21:
            return "On-Peak (Weekday)"
        else:
            return "Off-Peak (Weekday)"

def get_theme_for_bucket(bucket):
    """
    Return theme settings (background color and emoji) based on the current TOU bucket.
    For this version:
      - Super Off-Peak, Extra Off-Peak, and Off-Peak periods are encouraging for energy usage (✅).
      - On-Peak periods discourage usage (🚫).
    """
    if "On-Peak" in bucket:
        return {"bg_color": "#f0e5d8", "emoji": "🚫"}
    else:
        return {"bg_color": "#e0f7fa", "emoji": "✅"}

def main():
    st.set_page_config(page_title="TOU Bucket Tracker", layout="centered")
    now = datetime.now()
    current_bucket = get_tou_bucket(now)
    theme = get_theme_for_bucket(current_bucket)
    
    # Apply background color using custom CSS.
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {theme['bg_color']};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("SDG&E TOU-DR1 Residential Bucket Tracker")
    st.write("Current Time:", now.strftime("%Y-%m-%d %H:%M:%S"))
    st.header("Current TOU Bucket:")
    st.subheader(current_bucket)
    
    # Display a large emoji representing the current theme.
    st.markdown(
        f"<div style='font-size:100px; text-align:center;'>{theme['emoji']}</div>",
        unsafe_allow_html=True
    )
    
    st.info(
        "This app uses the TOU-DR1 Residential schedule with an extra off-peak window (10:00 a.m. – 2:00 p.m.) in March/April. "
        "Holidays are treated as weekends. "
        "Super Off-Peak and Off-Peak periods encourage energy usage (✅), while On-Peak periods discourage it (🚫)."
    )

if __name__ == "__main__":
    main()
