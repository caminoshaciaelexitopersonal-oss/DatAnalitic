from backend.core.state_store import Base, StateStore

def initialize_database():
    """
    Connects to the database and creates all tables based on the
    declarative base from the StateStore models.
    """
    print("--- Initializing Database Schema ---")

    # We instantiate a StateStore to get access to its engine
    state_store = StateStore()
    engine = state_store.engine

    try:
        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("All tables created successfully.")
    except Exception as e:
        print(f"An error occurred during table creation: {e}")

    print("--- Database Schema Initialized ---")

if __name__ == "__main__":
    initialize_database()
