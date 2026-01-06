"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in regional tournaments",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Swimming lessons and competitive swimming events",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and develop acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:30 PM",
            "max_participants": 30,
            "participants": ["isabella@mergington.edu", "mia@mergington.edu"]
        },
        "Art Class": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["james@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["charlotte@mergington.edu", "william@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and participate in science fairs",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["benjamin@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original)
    
    yield
    
    # Clean up after test
    activities.clear()
    activities.update(original)


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root path redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_activities_have_required_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_duplicate_participant(self, client):
        """Test signing up a participant who is already registered"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_full_activity(self, client):
        """Test signing up for a full activity"""
        # Fill up Chess Club (max 12 participants, currently has 2)
        for i in range(10):
            response = client.post(
                f"/activities/Chess%20Club/signup?email=student{i}@mergington.edu"
            )
            assert response.status_code == 200
        
        # Try to add one more (should fail)
        response = client.post(
            "/activities/Chess%20Club/signup?email=overflow@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "full" in data["detail"].lower()


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant"""
        # Verify participant exists
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]
        
        # Unregister participant
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a participant who is not registered"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_from_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_unregister_then_signup_again(self, client):
        """Test that a participant can sign up again after unregistering"""
        email = "michael@mergington.edu"
        
        # Unregister
        response = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Sign up again
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant is back
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]


class TestIntegrationScenarios:
    """Integration tests for common user workflows"""
    
    def test_complete_signup_workflow(self, client):
        """Test a complete signup workflow"""
        email = "testuser@mergington.edu"
        activity = "Programming Class"
        
        # Get initial state
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        after_signup = client.get("/activities")
        after_signup_data = after_signup.json()
        assert email in after_signup_data[activity]["participants"]
        assert len(after_signup_data[activity]["participants"]) == initial_count + 1
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        after_unregister = client.get("/activities")
        after_unregister_data = after_unregister.json()
        assert email not in after_unregister_data[activity]["participants"]
        assert len(after_unregister_data[activity]["participants"]) == initial_count
    
    def test_multiple_activities_same_user(self, client):
        """Test that one user can sign up for multiple activities"""
        email = "multitasker@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Class"]
        
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify user is in all activities
        all_activities = client.get("/activities").json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]
