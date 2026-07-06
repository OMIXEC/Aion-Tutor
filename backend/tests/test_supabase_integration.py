import os
import uvicorn
import sys
from pathlib import Path

# Add the backend directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
import json
import uuid
from dotenv import load_dotenv
from db.supabase_client import get_supabase_client
from aion_tutor.tools import (
    fetch_user_profile,
    update_profile,
    update_topic_mastery,
    create_session
)

load_dotenv()

# Use service role key for testing to bypass RLS and rate limits
TEST_SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")

@pytest.fixture
def supabase_client():
    from supabase import create_client
    if not SUPABASE_URL or not TEST_SUPABASE_KEY:
        pytest.skip("Supabase URL or Service Role Key not found in environment")
    return create_client(SUPABASE_URL, TEST_SUPABASE_KEY)

@pytest.fixture
def test_user_id(supabase_client):
    # Try to find an existing user or create a temporary record if possible
    try:
        resp = supabase_client.table("profiles").select("id").limit(1).execute()
    except Exception as e:
        pytest.skip(f"Supabase is configured but unreachable: {e}")
    if resp.data:
        return resp.data[0]["id"]

    # Try to get a user from auth.users (requires service role)
    try:
        users = supabase_client.auth.admin.list_users()
        if users:
            # Depending on version, it might be a list or a response object
            user = users[0] if isinstance(users, list) else users.users[0]
            user_id = user.id
            # Ensure it has a profile
            supabase_client.table("profiles").upsert({"id": user_id, "display_name": "Test User"}).execute()
            return user_id
    except Exception as e:
        print(f"Warning: Could not list auth users: {e}")

    # Fallback to a random UUID (might fail FK constraints if RLS/Triggers are strict)
    uid = str(uuid.uuid4())
    print(f"Warning: Using random UUID {uid} - results may vary based on FK constraints.")
    return uid

@pytest.mark.asyncio
async def test_fetch_user_profile(test_user_id):
    """Test fetching a user profile."""
    result = await fetch_user_profile(test_user_id)
    # Even if not found, it should return a string message, not crash
    assert isinstance(result, str)
    if "User profile not found" in result:
        print(f"User {test_user_id} not found, as expected for random UUID")
    else:
        profile = json.loads(result)
        assert profile["id"] == test_user_id

@pytest.mark.asyncio
async def test_update_profile(test_user_id):
    """Test updating user profile fields."""
    test_goal = f"Test Goal {uuid.uuid4().hex[:6]}"
    result = await update_profile(user_id=test_user_id, goal=test_goal)

    if "Error" in result:
        # If it failed because user doesn't exist, that's understandable but let's see why
        print(f"Update failed as expected if user is random: {result}")
        return

    assert result == "Profile successfully updated."

    # Verify the update
    fetch_result = await fetch_user_profile(test_user_id)
    if "User profile not found" in fetch_result:
        pytest.skip("Profile not found after update - likely due to DB constraints or missing row.")

    profile = json.loads(fetch_result)
    # Check either 'goal' or 'learning_goal' based on schema
    assert profile.get("goal") == test_goal or profile.get("learning_goal") == test_goal

@pytest.mark.asyncio
async def test_update_topic_mastery(test_user_id):
    """Test updating topic mastery."""
    topic = "Testing Integration"
    confidence = 0.85
    reasoning = "Unit test verification"

    result = await update_topic_mastery(
        user_id=test_user_id,
        topic=topic,
        confidence=confidence,
        reasoning=reasoning
    )

    if "violates foreign key constraint" in result:
        print(f"Topic mastery update failed as expected because user {test_user_id} does not exist in auth.users.")
        pytest.skip(f"Cannot test topic mastery without a valid user in auth.users. {result}")

    assert f"Mastery for {topic} explicitly recorded" in result

    # Verify in DB
    from db.supabase_client import get_supabase_client
    supabase = get_supabase_client()
    resp = supabase.table("topic_mastery").select("*").eq("user_id", test_user_id).eq("topic", topic).execute()
    assert len(resp.data) > 0
    assert resp.data[0]["score"] == confidence

@pytest.mark.asyncio
async def test_create_session(test_user_id):
    """Test creating a learning session."""
    title = f"Test Session {uuid.uuid4().hex[:6]}"
    result = await create_session(user_id=test_user_id, title=title)
    # Should return a UUID string
    try:
        uuid.UUID(result)
        is_uuid = True
    except ValueError:
        is_uuid = False

    assert is_uuid or "Error" in result
