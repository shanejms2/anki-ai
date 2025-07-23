# OAuth Setup Guide for Anki-AI

This guide will help you set up Google OAuth authentication for your Anki-AI application.

## 🚀 Quick Start

### 1. Supabase OAuth Configuration

1. **Go to your Supabase Dashboard**
   - Navigate to your project
   - Go to **Authentication** → **Providers**

2. **Enable OAuth Providers**
    - Enable **Google** provider
    - Configure the redirect URLs (see below)

### 2. Google OAuth Setup

#### Step 1: Create Google OAuth App
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**
5. Choose **Web application**
6. Add authorized redirect URIs:
   ```
   https://your-project-ref.supabase.co/auth/v1/callback
   http://localhost:3000/auth/callback (for development)
   ```
7. Copy the **Client ID** and **Client Secret**

#### Step 2: Configure Supabase
1. In Supabase Dashboard → **Authentication** → **Providers** → **Google**
2. Enable Google provider
3. Enter your **Client ID** and **Client Secret**
4. Save the configuration



## 🔧 Environment Variables

Add these to your `.env.local` file in the frontend:

```bash
# OAuth Configuration (optional - for additional security)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id
```

## 🧪 Testing OAuth

### 1. Start the Backend
```bash
cd anki-ai-backend
source venv/bin/activate
uvicorn app.main:app --reload
```

### 2. Start the Frontend
```bash
cd anki-ai
npm run dev
```

### 3. Test OAuth Flow
1. Go to `http://localhost:3000`
2. Click **Sign up** or **Sign in**
3. Click **Continue with Google** button
4. Complete the OAuth flow
5. You should be redirected back and logged in

## 🔒 Security Considerations

### 1. Redirect URLs
- Always use HTTPS in production
- Never use `localhost` in production redirects
- Keep your client secrets secure

### 2. Environment Variables
- Store sensitive data in environment variables
- Never commit secrets to version control
- Use different OAuth apps for development and production

### 3. User Data
- OAuth providers return basic user information
- Email and name are automatically extracted
- Username is generated from email if not provided

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid redirect URI"**
   - Check that your redirect URI matches exactly
   - Include both development and production URLs

2. **"OAuth login failed"**
   - Verify your client ID and secret are correct
   - Check that the provider is enabled in Supabase
   - Ensure your Supabase project is active

3. **"Provider not found"**
    - Make sure you've enabled the provider in Supabase
    - Check that the provider name matches exactly ("google")

### Debug Steps

1. **Check Supabase Logs**
   - Go to Supabase Dashboard → **Logs**
   - Look for authentication errors

2. **Check Browser Console**
   - Open Developer Tools
   - Look for network errors or JavaScript errors

3. **Check Backend Logs**
   - Monitor the backend console for error messages
   - Check for OAuth-related errors

## 📱 Production Deployment

### 1. Update Redirect URLs
When deploying to production, update your OAuth app redirect URLs:

**Google:**
```
https://your-domain.com/auth/callback
https://your-project-ref.supabase.co/auth/v1/callback
```

### 2. Environment Variables
Set production environment variables:

```bash
# Production environment
NEXT_PUBLIC_API_URL=https://your-api-domain.com
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_production_google_client_id
```

### 3. CORS Configuration
Update your backend CORS settings to include your production domain:

```python
# In app/core/config.py
allowed_origins: str = "https://your-domain.com,http://localhost:3000"
```

## 🎯 Features Implemented

✅ **Google OAuth** - Sign in/up with Google account  
✅ **Automatic Profile Creation** - User profiles created automatically  
✅ **Seamless Integration** - Works with existing auth system  
✅ **Error Handling** - Proper error messages and fallbacks  
✅ **Loading States** - Visual feedback during OAuth flow  
✅ **Responsive Design** - Works on mobile and desktop  

## 🔄 OAuth Flow

1. **User clicks OAuth button**
2. **Frontend requests OAuth URL from backend**
3. **User is redirected to OAuth provider**
4. **User authorizes the application**
5. **OAuth provider redirects back with code**
6. **Backend exchanges code for session**
7. **User profile is created/retrieved**
8. **User is logged in and redirected to app**

## 📚 Additional Resources

- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2)

---

**OAuth Setup Status**: ✅ **COMPLETE**

Your Anki-AI application now supports social login with Google and GitHub! 