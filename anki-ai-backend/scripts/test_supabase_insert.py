from supabase import create_client
import uuid
from datetime import datetime

# Replace with your actual values
SUPABASE_URL = "https://cgpjekmxzuztwyghpamk.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNncGpla214enV6dHd5Z2hwYW1rIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Mjk0MjEzNiwiZXhwIjoyMDY4NTE4MTM2fQ.fPhb8KKClfYIHWfaJ0gjrSO82jIhCf0k0TbEfIkqaKA"

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

now = datetime.utcnow().isoformat()
card = {
    "id": str(uuid.uuid4()),
    "user_id": "647428f1-da36-43d9-b3f0-63e22ebd1e27",  # Use a valid user UUID from your users table
    "front": "Test card front (script)",
    "back": "Test card back (script)",
    "interval": 1,
    "ease": 2.5,
    "next_review": now,
    "created_at": now,
    "updated_at": now
}

result = supabase.table("cards").insert(card).execute()
print(result)
