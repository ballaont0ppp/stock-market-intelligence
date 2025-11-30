# Brand Identity Cleanup Summary

This document summarizes the removal of brand-specific identity and logos from the repository.

## Changes Made

### 1. README.md
- ✅ Removed all GitHub badges linking to original repository
- ✅ Removed original author information (Kaushik Jadhav)
- ✅ Removed links to original author's social media profiles
- ✅ Removed demo video with branded content
- ✅ Removed external screenshot links
- ✅ Changed admin email from `stockpredictorapp@gmail.com` to generic placeholder
- ✅ Updated title to "Stock Market Prediction & Portfolio Management Platform"
- ✅ Simplified to use local screenshots only

### 2. CITATION.cff
- ✅ Removed original author information
- ✅ Removed DOI and ORCID references
- ✅ Removed GitHub repository URL
- ✅ Updated title to generic name
- ✅ Added MIT license reference

### 3. CONTRIBUTING.md
- ✅ Removed link to original GitHub repository
- ✅ Changed to reference local README.md

### 4. HTML Templates
- ✅ Replaced "StockFlow" brand name with "Portfolio" in sidebar (app/templates/base.html)
- ✅ Updated page title to "Stock Portfolio Platform" (app/templates/base.html)
- ✅ Removed "StockFlow" from registration page subtitle (app/templates/auth/register.html)
- ✅ Removed "StockFlow" from login page subtitle (app/templates/auth/login.html)

## Files Still Containing Brand References

### wordpress.sql
⚠️ **Note**: The `wordpress.sql` file contains multiple references to:
- "Gyanberry" (original brand name)
- Email addresses: `kaushikjadhav293@gmail.com`, `kaushikjadhav01@gmail.com`
- User accounts and WordPress configuration

**Recommendation**: This is a WordPress database dump. If you're not using WordPress, you can delete this file entirely. If you are using it, you'll need to:
1. Import the database
2. Use WordPress admin panel to change site name, email addresses, and user information
3. Export a fresh database dump

### screenshots/
The screenshots folder contains images that may show branded content. Consider:
- Taking new screenshots after rebranding
- Or removing screenshots entirely if not needed

## Recommended Next Steps

1. **Choose Your Brand Name**: Decide on a name for your platform and update:
   - `app/templates/base.html` (sidebar logo and page title)
   - `README.md` (main title)
   - Any other marketing materials

2. **Update Screenshots**: 
   - Take new screenshots without branded content
   - Or remove the screenshots folder if not needed

3. **WordPress Database** (if using):
   - Import `wordpress.sql`
   - Update site settings in WordPress admin
   - Change all email addresses
   - Create new admin user
   - Export fresh database

4. **Environment Variables**:
   - Update `.env` file with your own email addresses
   - Update any API keys or credentials

5. **Git History** (optional):
   - Consider squashing commits to remove historical brand references
   - Or start fresh with a new repository

## Files You Can Safely Delete

If you're not using certain features, you can delete:
- `wordpress.sql` - if not using WordPress
- `screenshots/` - if you'll take new screenshots
- `CITATION.cff` - if not publishing academically
- Old documentation files with brand references

## Clean Slate Checklist

- [x] README.md cleaned
- [x] CITATION.cff cleaned
- [x] CONTRIBUTING.md cleaned
- [x] HTML templates cleaned
- [ ] WordPress database (manual update needed)
- [ ] Screenshots (manual replacement needed)
- [ ] Choose new brand name
- [ ] Update environment variables
