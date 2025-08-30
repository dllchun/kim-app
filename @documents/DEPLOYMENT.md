# Streamlit Community Cloud Deployment Guide

## Prerequisites ✅

All files are ready for deployment:

- ✅ `main_app.py` - Entry point file
- ✅ `requirements.txt` - Python dependencies
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `packages.txt` - System packages (if needed)
- ✅ `.gitignore` - Git ignore rules
- ✅ `README.md` - Project documentation
- ✅ Git repository initialized

## Deployment Steps

### 1. Push to GitHub
```bash
# Add all files to git
git add .

# Commit changes
git commit -m "Add battery synergy analyzer app for Streamlit Cloud deployment"

# Create GitHub repository and push
git remote add origin https://github.com/your-username/battery-synergy-analyzer.git
git push -u origin main
```

### 2. Deploy to Streamlit Cloud

1. **Visit**: https://share.streamlit.io/
2. **Sign in** with GitHub account
3. **Click "New app"**
4. **Configure**:
   - Repository: `your-username/battery-synergy-analyzer`
   - Branch: `main`
   - Main file path: `main_app.py`
   - App URL: `battery-synergy-analyzer` (or custom name)

### 3. Deployment Settings

**Advanced Settings** (optional):
- **Python version**: 3.11
- **Environment variables**: None needed
- **Secrets**: None required for this app

## Important Files for Deployment

### `main_app.py`
- ✅ Main entry point
- ✅ Imports all modules correctly
- ✅ Handles Streamlit configuration

### `requirements.txt`
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
scipy>=1.10.0
scikit-learn>=1.3.0
```

### `.streamlit/config.toml`
- ✅ Optimizes performance for cloud
- ✅ Sets theme colors
- ✅ Configures upload limits

### `packages.txt`
- ✅ Empty (no system packages needed)
- ✅ Ready for future system dependencies

## Troubleshooting

### Common Issues

#### Import Errors
- **Problem**: Module not found
- **Solution**: Check all imports use relative paths in `synergy_app/`

#### Memory Issues  
- **Problem**: App crashes with large datasets
- **Solution**: Limit data points in `config/settings.py`

#### Slow Loading
- **Problem**: App takes long to start
- **Solution**: Streamlit Cloud sometimes needs 30-60 seconds for first load

### Performance Optimization

#### For Cloud Deployment:
1. **Caching**: Add `@st.cache_data` to expensive functions
2. **Session State**: Minimize large objects in session state
3. **Memory**: Keep datasets under 100MB
4. **Dependencies**: Only include required packages

## Post-Deployment

### App URL Structure
Your app will be available at:
```
https://your-username-battery-synergy-analyzer-main-app-xyz123.streamlit.app
```

### Monitoring
- **Logs**: Available in Streamlit Cloud dashboard
- **Usage**: Analytics provided by Streamlit
- **Updates**: Automatic deployment on git push

### Sharing
- App is public by default
- Share URL with researchers
- No authentication required
- Works on mobile devices

## Advanced Configuration

### Custom Domain (Optional)
Contact Streamlit support for custom domain setup

### Private Repository
- Requires Streamlit Teams plan
- Same deployment process
- Access control available

### Environment Variables
Add in Streamlit Cloud dashboard if needed:
```
# Example secrets (not needed for this app)
API_KEY = "your-secret-key"
```

## Maintenance

### Updates
```bash
# Make changes locally
git add .
git commit -m "Update feature X"
git push origin main
# App automatically redeploys
```

### Rollback
Use GitHub to revert commits if needed - Streamlit Cloud will auto-deploy the reverted state.

## Support

- **Streamlit Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **Community Forum**: https://discuss.streamlit.io/
- **Status Page**: https://streamlit.statuspage.io/