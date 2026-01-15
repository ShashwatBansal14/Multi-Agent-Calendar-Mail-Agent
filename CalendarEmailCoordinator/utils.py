from datetime import datetime
import pytz

def get_current_datetime():
    """Returns current date and time in Indian Standard Time (IST)."""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S %Z')