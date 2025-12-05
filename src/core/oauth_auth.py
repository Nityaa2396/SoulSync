"""
OAuth Authentication for SoulSync
Supports Google and GitHub login
"""

import streamlit as st
import os
from typing import Optional, Dict
import requests
from urllib.parse import urlencode


class OAuthProvider:
    """Base class for OAuth providers."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self) -> str:
        """Get URL to redirect user for OAuth authorization."""
        raise NotImplementedError
    
    def get_user_info(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for user info."""
        raise NotImplementedError


class GoogleOAuth(OAuthProvider):
    """Google OAuth 2.0 provider."""
    
    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_authorization_url(self) -> str:
        """Get Google OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "select_account"
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"
    
    def get_user_info(self, code: str) -> Optional[Dict]:
        """Exchange Google auth code for user info."""
        # Exchange code for access token
        token_data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        token_response = requests.post(self.TOKEN_URL, data=token_data)
        
        if token_response.status_code != 200:
            return None
        
        access_token = token_response.json().get("access_token")
        
        # Get user info
        headers = {"Authorization": f"Bearer {access_token}"}
        user_response = requests.get(self.USER_INFO_URL, headers=headers)
        
        if user_response.status_code != 200:
            return None
        
        user_data = user_response.json()
        
        return {
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "provider": "google",
            "provider_id": user_data.get("id"),
            "picture": user_data.get("picture")
        }


class GitHubOAuth(OAuthProvider):
    """GitHub OAuth provider."""
    
    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_INFO_URL = "https://api.github.com/user"
    EMAIL_URL = "https://api.github.com/user/emails"
    
    def get_authorization_url(self) -> str:
        """Get GitHub OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user:email"
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"
    
    def get_user_info(self, code: str) -> Optional[Dict]:
        """Exchange GitHub auth code for user info."""
        # Exchange code for access token
        token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        headers = {"Accept": "application/json"}
        token_response = requests.post(self.TOKEN_URL, data=token_data, headers=headers)
        
        if token_response.status_code != 200:
            return None
        
        access_token = token_response.json().get("access_token")
        
        # Get user info
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        user_response = requests.get(self.USER_INFO_URL, headers=headers)
        
        if user_response.status_code != 200:
            return None
        
        user_data = user_response.json()
        
        # Get email (might be private)
        email = user_data.get("email")
        if not email:
            email_response = requests.get(self.EMAIL_URL, headers=headers)
            if email_response.status_code == 200:
                emails = email_response.json()
                # Get primary email
                for email_obj in emails:
                    if email_obj.get("primary"):
                        email = email_obj.get("email")
                        break
        
        return {
            "email": email,
            "name": user_data.get("name") or user_data.get("login"),
            "provider": "github",
            "provider_id": str(user_data.get("id")),
            "picture": user_data.get("avatar_url")
        }


# ═══════════════════════════════════════════════════════════
# STREAMLIT OAUTH HELPERS
# ═══════════════════════════════════════════════════════════

def render_oauth_buttons():
    """
    Render OAuth login buttons.
    Call this on your login page.
    """
    st.markdown("### Or sign in with:")
    
    col1, col2 = st.columns(2)
    
    # Google Sign In
    with col1:
        google_client_id = os.getenv("GOOGLE_CLIENT_ID")
        google_redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        
        if google_client_id and google_redirect_uri:
            google = GoogleOAuth(
                client_id=google_client_id,
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
                redirect_uri=google_redirect_uri
            )
            
            auth_url = google.get_authorization_url()
            
            st.markdown(f"""
            <a href="{auth_url}" target="_self">
                <button style="
                    width: 100%;
                    padding: 10px;
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                ">
                    🔵 Google
                </button>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.button("🔵 Google", disabled=True, help="Not configured")
    
    # GitHub Sign In
    with col2:
        github_client_id = os.getenv("GITHUB_CLIENT_ID")
        github_redirect_uri = os.getenv("GITHUB_REDIRECT_URI")
        
        if github_client_id and github_redirect_uri:
            github = GitHubOAuth(
                client_id=github_client_id,
                client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
                redirect_uri=github_redirect_uri
            )
            
            auth_url = github.get_authorization_url()
            
            st.markdown(f"""
            <a href="{auth_url}" target="_self">
                <button style="
                    width: 100%;
                    padding: 10px;
                    background: #24292e;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                ">
                    ⚫ GitHub
                </button>
            </a>
            """, unsafe_allow_html=True)
        else:
            st.button("⚫ GitHub", disabled=True, help="Not configured")


def handle_oauth_callback():
    """
    Handle OAuth callback after user authorizes.
    Call this at the start of your app.
    
    Returns:
        User dict if OAuth successful, None otherwise
    """
    from supabase_client import get_supabase_client
    
    # Check for OAuth callback parameters
    query_params = st.query_params
    
    code = query_params.get("code")
    provider_param = query_params.get("state")  # We can use state to track provider
    
    if not code:
        return None
    
    # Determine which provider based on referrer or state
    # For now, we'll try both
    
    db = get_supabase_client()
    
    # Try Google first
    google_client_id = os.getenv("GOOGLE_CLIENT_ID")
    if google_client_id:
        google = GoogleOAuth(
            client_id=google_client_id,
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
        )
        
        user_info = google.get_user_info(code)
        
        if user_info:
            # Create or get user
            user = db.create_oauth_user(
                email=user_info["email"],
                provider="google",
                provider_id=user_info["provider_id"]
            )
            
            # Clear query params
            st.query_params.clear()
            
            return user
    
    # Try GitHub
    github_client_id = os.getenv("GITHUB_CLIENT_ID")
    if github_client_id:
        github = GitHubOAuth(
            client_id=github_client_id,
            client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
            redirect_uri=os.getenv("GITHUB_REDIRECT_URI")
        )
        
        user_info = github.get_user_info(code)
        
        if user_info:
            # Create or get user
            user = db.create_oauth_user(
                email=user_info["email"],
                provider="github",
                provider_id=user_info["provider_id"]
            )
            
            # Clear query params
            st.query_params.clear()
            
            return user
    
    return None


# ═══════════════════════════════════════════════════════════
# SETUP INSTRUCTIONS
# ═══════════════════════════════════════════════════════════

"""
GOOGLE OAUTH SETUP:
1. Go to: https://console.cloud.google.com/
2. Create new project: "SoulSync"
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: https://your-app.streamlit.app/
5. Copy Client ID and Client Secret
6. Add to Streamlit secrets:
   GOOGLE_CLIENT_ID = "..."
   GOOGLE_CLIENT_SECRET = "..."
   GOOGLE_REDIRECT_URI = "https://your-app.streamlit.app/"

GITHUB OAUTH SETUP:
1. Go to: https://github.com/settings/developers
2. Click "New OAuth App"
3. Application name: SoulSync
4. Homepage URL: https://your-app.streamlit.app
5. Authorization callback URL: https://your-app.streamlit.app/
6. Copy Client ID and Client Secret
7. Add to Streamlit secrets:
   GITHUB_CLIENT_ID = "..."
   GITHUB_CLIENT_SECRET = "..."
   GITHUB_REDIRECT_URI = "https://your-app.streamlit.app/"
"""