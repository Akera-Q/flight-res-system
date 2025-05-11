import hashlib
import secrets
import binascii
from models import User, Base
from database import engine, SessionLocal

def setup_database():
    """Create all tables before tests"""
    Base.metadata.create_all(bind=engine)

def teardown_database():
    """Clean up after tests"""
    Base.metadata.drop_all(bind=engine)

def test_user_creation():
    """Test user creation and password hashing"""
    db = SessionLocal()
    try:
        # Test data
        username = "testuser"
        email = "test@example.com"
        password = "supersecret123"
        
        # Create user with plain password (let model handle hashing)
        user = User(
            username=username,
            email=email,
            password=password  # Using plain password
        )

        # Add to database
        db.add(user)
        db.commit()
        db.refresh(user)

        # Verify attributes
        assert user.username == username
        assert user.email == email
        assert user.hashed_password is not None
        assert user.salt is not None
        assert user.hashed_password != password  # Password shouldn't be stored plain
        assert user.is_active is True

        # Verify password
        assert user.verify_password(password) is True
        assert user.verify_password("wrongpassword") is False

        print("✅ User creation passed")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def test_password_hashing():
    """Test password hashing consistency"""
    password = "testpassword123"
    
    # Hash twice with same password
    hash1, salt1 = User.hash_password(password)
    hash2, salt2 = User.hash_password(password)
    
    # Should produce different hashes (different salts)
    assert hash1 != hash2
    assert salt1 != salt2
    
    # But both should verify correctly
    temp_user = User(username="temp", email="temp@test.com", password=password)
    assert temp_user.verify_password(password) is True
    print("✅ Password hashing passed")

def test_existing_user():
    """Test duplicate user prevention"""
    db = SessionLocal()
    try:
        # Create first user
        user1 = User(
            username="existinguser",
            email="user1@example.com",
            password="password123"
        )
        db.add(user1)
        db.commit()

        # Try to create duplicate
        try:
            user2 = User(
                username="existinguser",  # Same username
                email="user2@example.com",
                password="password456"
            )
            db.add(user2)
            db.commit()
            assert False, "Should have raised an integrity error"
        except Exception as e:
            db.rollback()
            assert "unique" in str(e).lower(), "Should fail on unique constraint"

        print("✅ Duplicate user prevention passed")
    finally:
        db.close()

if __name__ == "__main__":
    try:
        setup_database()
        test_user_creation()
        test_password_hashing()
        test_existing_user()
    finally:
        teardown_database()
    print("All tests completed successfully!")