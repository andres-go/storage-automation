from dotenv import load_dotenv
load_dotenv()
import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

email: str = "andres.gonzalez@kurobiautomation.com"
password: str = "12345678"
# session = supabase.auth.sign_up(
#     {
#         "email": email, 
#         "password": password,
#     }
# )

session = None
try:
    # Attempt to sign in with the provided email and password
    session = supabase.auth.sign_in_with_password(
        {
            "email": email, 
            "password": password,
        }
    )
except Exception as e:
    # If an error occurs, print the error message
    print(f"Error signing in: {e}")

supabase.auth.sign_out()
print(session)