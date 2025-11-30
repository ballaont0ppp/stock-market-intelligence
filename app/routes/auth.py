"""
Authentication Routes
Handles user registration, login, logout, and profile management
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.services.auth_service import AuthService
from app.forms.auth_forms import RegistrationForm, LoginForm, ProfileForm, PasswordChangeForm
from app.utils.rate_limiter import login_rate_limiter

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Register user
            user, error = AuthService.register_user(
                email=form.email.data,
                password=form.password.data,
                full_name=form.full_name.data
            )
            
            if error:
                flash(error, 'error')
            else:
                # Auto-login after registration
                AuthService.create_session(user)
                flash(f'Welcome {user.full_name}! Your account has been created successfully.', 'success')
                return redirect(url_for('dashboard.index'))
                
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        
        # Check rate limiting
        is_limited, remaining_time = login_rate_limiter.is_rate_limited(email)
        if is_limited:
            minutes = remaining_time // 60
            seconds = remaining_time % 60
            flash(f'Too many failed login attempts. Please try again in {minutes} minutes and {seconds} seconds.', 'error')
            return render_template('auth/login.html', form=form)
        
        try:
            # Authenticate user
            user = AuthService.authenticate_user(
                email=email,
                password=form.password.data
            )
            
            if user:
                # Reset rate limiter on successful login
                login_rate_limiter.reset_attempts(email)
                
                # Create session
                AuthService.create_session(user, remember=form.remember_me.data)
                flash(f'Welcome back, {user.full_name or user.email}!', 'success')
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                if next_page and next_page.startswith('/'):
                    return redirect(next_page)
                return redirect(url_for('dashboard.index'))
            else:
                # Record failed attempt
                login_rate_limiter.record_failed_attempt(email)
                remaining = login_rate_limiter.get_remaining_attempts(email)
                
                if remaining > 0:
                    flash(f'Invalid email or password. {remaining} attempts remaining.', 'error')
                else:
                    flash('Too many failed login attempts. Your account has been temporarily locked.', 'error')
                
        except ValueError as e:
            # Record failed attempt for suspended accounts too
            login_rate_limiter.record_failed_attempt(email)
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'error')
    
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    AuthService.destroy_session()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    profile_form = ProfileForm()
    password_form = PasswordChangeForm()
    
    # Handle profile update
    if profile_form.validate_on_submit() and 'update_profile' in request.form:
        try:
            # Prepare notification preferences
            notification_prefs = {
                'dividends': profile_form.notify_dividends.data,
                'price_changes': profile_form.notify_price_changes.data,
                'weekly_summary': profile_form.notify_weekly_summary.data
            }
            
            # Update profile
            AuthService.update_profile(
                user_id=current_user.user_id,
                data={
                    'full_name': profile_form.full_name.data,
                    'risk_tolerance': profile_form.risk_tolerance.data,
                    'investment_goals': profile_form.investment_goals.data,
                    'preferred_sectors': profile_form.preferred_sectors.data,
                    'notification_preferences': notification_prefs
                }
            )
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('auth.profile'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while updating your profile. Please try again.', 'error')
    
    # Handle password change
    if password_form.validate_on_submit() and 'change_password' in request.form:
        try:
            AuthService.change_password(
                user_id=current_user.user_id,
                old_password=password_form.current_password.data,
                new_password=password_form.new_password.data
            )
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash('An error occurred while changing your password. Please try again.', 'error')
    
    # Pre-populate form with current user data
    if request.method == 'GET':
        profile_form.full_name.data = current_user.full_name
        profile_form.risk_tolerance.data = current_user.risk_tolerance
        profile_form.investment_goals.data = current_user.investment_goals
        profile_form.preferred_sectors.data = current_user.preferred_sectors or []
        
        # Load notification preferences
        if current_user.notification_preferences:
            prefs = current_user.notification_preferences
            profile_form.notify_dividends.data = prefs.get('dividends', False)
            profile_form.notify_price_changes.data = prefs.get('price_changes', False)
            profile_form.notify_weekly_summary.data = prefs.get('weekly_summary', False)
    
    return render_template('auth/profile.html', 
                         profile_form=profile_form, 
                         password_form=password_form)
