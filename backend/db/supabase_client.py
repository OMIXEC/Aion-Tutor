import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logging.error(f"Failed to initialize Supabase client: {e}")
else:
    logging.warning("SUPABASE_URL or SUPABASE_KEY not found in environment. Database calls will fail.")

def get_supabase_client() -> Client:
    if not supabase:
        raise ValueError("Supabase client is not initialized. Please set SUPABASE_URL and SUPABASE_KEY.")
    return supabase
