from supabase import create_client, Client

from config.settings import SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_ANON_KEY

_supabase: Client | None = None


def get_supabase() -> Client:
    """Return a Supabase client authenticated with the service_role key (bypasses RLS)."""
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    return _supabase


def get_anon_client() -> Client:
    """Return a Supabase client with the anon key (respects RLS)."""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)