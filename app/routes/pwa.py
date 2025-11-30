"""
PWA (Progressive Web App) routes
Handles offline page and PWA-related endpoints
"""
from flask import Blueprint, render_template

bp = Blueprint('pwa', __name__)


@bp.route('/offline')
def offline():
    """
    Offline page
    Displayed when the user is offline and tries to access a page
    that is not cached by the service worker
    
    Returns:
        Rendered offline.html template
    """
    return render_template('offline.html')
