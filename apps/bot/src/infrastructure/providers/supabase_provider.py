"""
Supabase client provider for dependency injection.
"""
from supabase import create_client, Client
from config.settings import settings


class SupabaseProvider:
    """Factory for creating Supabase client instances."""
    
    _client: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create a Supabase client instance (singleton pattern)."""
        if cls._client is None:
            if not settings.supabase_url or not settings.supabase_service_key:
                raise ValueError("Supabase configuration missing: SUPABASE_URL and SUPABASE_SERVICE_KEY required")
            
            cls._client = create_client(settings.supabase_url, settings.supabase_service_key)
        
        return cls._client
    
    @classmethod
    def create_client(cls) -> Client:
        """Create a new Supabase client instance (factory pattern)."""
        if not settings.supabase_url or not settings.supabase_service_key:
            raise ValueError("Supabase configuration missing: SUPABASE_URL and SUPABASE_SERVICE_KEY required")
        
        return create_client(settings.supabase_url, settings.supabase_service_key)
