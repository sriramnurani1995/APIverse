import unittest
from unittest.mock import MagicMock
from werkzeug.security import generate_password_hash
import sys
import os



from model.model_datastore import model  


class TestVerifyUser(unittest.TestCase):
    def setUp(self):
        """Setup mock model instance."""
        self.model = model()
        self.model.get_user = MagicMock()  # Mock database call to avoid real DB dependency

    def test_verify_user_success(self):
        """Test successful login with correct credentials."""
        email = "test@pdx.edu"
        password = "securepassword"
        hashed_password = generate_password_hash(password)

        # Mock get_user return value with correct credentials
        self.model.get_user.return_value = {"email": email, "password": hashed_password}

        # Call the function
        result = self.model.verify_user(email, password)

        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result["email"], email)

    def test_verify_user_wrong_password(self):
        """Test failed login due to incorrect password."""
        email = "test@pdx.edu"
        correct_password = "securepassword"
        wrong_password = "wrongpassword"
        hashed_password = generate_password_hash(correct_password)

        # Mock get_user return value with correct credentials
        self.model.get_user.return_value = {"email": email, "password": hashed_password}

        # Call the function with the wrong password
        result = self.model.verify_user(email, wrong_password)

        # Assertions
        self.assertIsNone(result)

    def test_verify_user_nonexistent_user(self):
        """Test login with a non-existent user."""
        email = "nonexistent@pdx.edu"
        password = "somepassword"

        # Mock get_user to return None (user not found)
        self.model.get_user.return_value = None

        # Call the function
        result = self.model.verify_user(email, password)

        # Assertions
        self.assertIsNone(result)

# Run the tests if executed directly
if __name__ == "__main__":
    unittest.main()
