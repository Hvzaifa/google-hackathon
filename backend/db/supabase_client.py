import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class MockResult:
    def __init__(self, data):
        self.data = data

class MockQueryBuilder:
    def __init__(self, data=None):
        self._data = data or []
    def select(self, *args, **kwargs): return self
    def insert(self, *args, **kwargs): return self
    def update(self, *args, **kwargs): return self
    def eq(self, *args, **kwargs): return self
    def gte(self, *args, **kwargs): return self
    def lte(self, *args, **kwargs): return self
    def neq(self, *args, **kwargs): return self
    def in_(self, *args, **kwargs): return self
    def order(self, *args, **kwargs): return self
    def execute(self): return MockResult(self._data)

class MockSupabaseClient:
    def table(self, table_name: str):
        if table_name == "provider_reputation":
            return MockQueryBuilder([{"reputation_score": 0.8, "future_matching_impact": 0}])
        elif table_name == "bookings":
            return MockQueryBuilder([{"id": "mock-booking-id", "status": "confirmed"}])
        return MockQueryBuilder([{}])

supabase = MockSupabaseClient()
if SUPABASE_URL and isinstance(SUPABASE_URL, str) and ".supabase.co" in SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)