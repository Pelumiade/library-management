def test_settings_are_patched():
    """Verify that the settings patch is working"""
    from app.config import settings
    assert settings.POSTGRES_SERVER == "localhost"
    assert settings.DATABASE_URL == "sqlite:///./test.db"

def test_db_session(db_session):
    """Verify that the database session fixture works"""
    assert db_session is not None