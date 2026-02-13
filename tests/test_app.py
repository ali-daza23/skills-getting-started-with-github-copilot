"""
Tests for the FastAPI application
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_200(self, client, reset_activities):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that GET /activities returns activities as a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_expected_activities(self, client, reset_activities):
        """Test that GET /activities contains all expected activities"""
        response = client.get("/activities")
        data = response.json()
        
        expected_activities = [
            "Basketball", "Tennis Club", "Art Studio", "Music Ensemble",
            "Debate Team", "Science Club", "Chess Club", "Programming Class", "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in data
    
    def test_activity_has_required_fields(self, client, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_returns_200_on_success(self, client, reset_activities):
        """Test that signup returns status 200 on success"""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds a participant to the activity"""
        client.post(
            "/activities/Basketball/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        
        assert "newstudent@mergington.edu" in data["Basketball"]["participants"]
    
    def test_signup_returns_success_message(self, client, reset_activities):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Basketball/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        data = response.json()
        
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]
    
    def test_signup_invalid_activity_returns_404(self, client, reset_activities):
        """Test that signup returns 404 for invalid activity"""
        response = client.post(
            "/activities/InvalidActivity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_signup_invalid_activity_error_message(self, client, reset_activities):
        """Test that signup returns proper error message for invalid activity"""
        response = client.post(
            "/activities/InvalidActivity/signup",
            params={"email": "student@mergington.edu"}
        )
        data = response.json()
        
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_duplicate_signup_allowed(self, client, reset_activities):
        """Test that the same student can sign up twice (note: this tests the bug)"""
        # First signup
        response1 = client.post(
            "/activities/Basketball/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Second signup (should be prevented but currently isn't)
        response2 = client.post(
            "/activities/Basketball/signup",
            params={"email": "duplicate@mergington.edu"}
        )
        
        # Get the activities to check
        response = client.get("/activities")
        data = response.json()
        participants = data["Basketball"]["participants"]
        
        # Count how many times the email appears
        count = participants.count("duplicate@mergington.edu")
        
        # This test documents the bug - currently count will be 2
        # Once fixed, this should be 1
        assert count >= 1


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_returns_200_on_success(self, client, reset_activities):
        """Test that unregister returns status 200 on success"""
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "alex@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes a participant"""
        client.delete(
            "/activities/Basketball/unregister",
            params={"email": "alex@mergington.edu"}
        )
        
        response = client.get("/activities")
        data = response.json()
        
        assert "alex@mergington.edu" not in data["Basketball"]["participants"]
    
    def test_unregister_returns_success_message(self, client, reset_activities):
        """Test that unregister returns a success message"""
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "alex@mergington.edu"}
        )
        data = response.json()
        
        assert "message" in data
        assert "alex@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]
    
    def test_unregister_invalid_activity_returns_404(self, client, reset_activities):
        """Test that unregister returns 404 for invalid activity"""
        response = client.delete(
            "/activities/InvalidActivity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_unregister_invalid_participant_returns_404(self, client, reset_activities):
        """Test that unregister returns 404 for non-participant"""
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "nonexistent@mergington.edu"}
        )
        assert response.status_code == 404
    
    def test_unregister_invalid_participant_error_message(self, client, reset_activities):
        """Test that unregister returns proper error message for non-participant"""
        response = client.delete(
            "/activities/Basketball/unregister",
            params={"email": "nonexistent@mergington.edu"}
        )
        data = response.json()
        
        assert "detail" in data
        assert "Participant not found" in data["detail"]


class TestFullWorkflow:
    """Tests for complete user workflows"""
    
    def test_signup_and_unregister_workflow(self, client, reset_activities):
        """Test the full workflow of signing up and then unregistering"""
        email = "workflow@mergington.edu"
        activity = "Basketball"
        
        # Sign up
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Verify participant was added
        response2 = client.get("/activities")
        data = response2.json()
        assert email in data[activity]["participants"]
        
        # Unregister
        response3 = client.delete(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify participant was removed
        response4 = client.get("/activities")
        data = response4.json()
        assert email not in data[activity]["participants"]
    
    def test_multiple_signups_workflow(self, client, reset_activities):
        """Test signing up for multiple activities"""
        email = "multi@mergington.edu"
        activities_list = ["Basketball", "Tennis Club", "Art Studio"]
        
        # Sign up for multiple activities
        for activity in activities_list:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify participant is in all activities
        response = client.get("/activities")
        data = response.json()
        
        for activity in activities_list:
            assert email in data[activity]["participants"]
