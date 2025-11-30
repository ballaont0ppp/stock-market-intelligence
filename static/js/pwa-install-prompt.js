/**
 * PWA Installation Prompt Handler
 * Manages the beforeinstallprompt event and custom install button
 * 
 * Features:
 * - Captures beforeinstallprompt event
 * - Shows custom install button when app is installable
 * - Handles installation flow and success feedback
 * - Stores installation preference to avoid repeated prompts
 */

class PWAInstallPrompt {
  constructor() {
    this.deferredPrompt = null;
    this.installButton = null;
    this.installContainer = null;
    this.isInstalled = false;
    this.installAttempted = false;
    
    this.init();
  }

  /**
   * Initialize PWA install prompt handler
   */
  init() {
    // Check if app is already installed
    this.checkIfInstalled();
    
    // Listen for beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => this.handleBeforeInstallPrompt(e));
    
    // Listen for app installed event
    window.addEventListener('appinstalled', () => this.handleAppInstalled());
    
    // Create install button UI
    this.createInstallButton();
    
    // Check display mode to determine if running as PWA
    this.checkDisplayMode();
    
    console.log('[PWA Install] Initialized');
  }

  /**
   * Handle beforeinstallprompt event
   * This event fires when the browser detects the app is installable
   */
  handleBeforeInstallPrompt(e) {
    console.log('[PWA Install] beforeinstallprompt event fired');
    
    // Prevent the mini-infobar from appearing
    e.preventDefault();
    
    // Store the event for later use
    this.deferredPrompt = e;
    
    // Show the install button
    this.showInstallButton();
  }

  /**
   * Handle app installed event
   * This event fires when the user successfully installs the app
   */
  handleAppInstalled() {
    console.log('[PWA Install] App installed successfully');
    
    // Clear the deferred prompt
    this.deferredPrompt = null;
    
    // Hide the install button
    this.hideInstallButton();
    
    // Mark as installed
    this.isInstalled = true;
    
    // Store installation state
    localStorage.setItem('pwa_installed', 'true');
    
    // Show success message
    this.showInstallationSuccess();
  }

  /**
   * Create custom install button UI
   */
  createInstallButton() {
    // Check if button already exists
    if (document.getElementById('pwa-install-button')) {
      this.installButton = document.getElementById('pwa-install-button');
      this.installContainer = document.getElementById('pwa-install-container');
      return;
    }

    // Create container for install button
    this.installContainer = document.createElement('div');
    this.installContainer.id = 'pwa-install-container';
    this.installContainer.className = 'pwa-install-container';
    this.installContainer.style.display = 'none';

    // Create install button
    this.installButton = document.createElement('button');
    this.installButton.id = 'pwa-install-button';
    this.installButton.className = 'btn btn-primary pwa-install-button';
    this.installButton.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7 10 12 15 17 10"></polyline>
        <line x1="12" y1="15" x2="12" y2="3"></line>
      </svg>
      <span>Install App</span>
    `;
    this.installButton.title = 'Install this app on your device';
    this.installButton.addEventListener('click', () => this.handleInstallClick());

    // Create close button
    const closeButton = document.createElement('button');
    closeButton.className = 'btn btn-ghost pwa-install-close';
    closeButton.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    `;
    closeButton.title = 'Dismiss';
    closeButton.addEventListener('click', () => this.dismissInstallPrompt());

    // Add buttons to container
    this.installContainer.appendChild(this.installButton);
    this.installContainer.appendChild(closeButton);

    // Insert container into the page
    // Try to insert after topbar if it exists, otherwise at the beginning of body
    const topbar = document.querySelector('.topbar');
    if (topbar && topbar.parentNode) {
      topbar.parentNode.insertBefore(this.installContainer, topbar.nextSibling);
    } else {
      document.body.insertBefore(this.installContainer, document.body.firstChild);
    }

    console.log('[PWA Install] Install button created');
  }

  /**
   * Show install button
   */
  showInstallButton() {
    if (this.installContainer) {
      this.installContainer.style.display = 'flex';
      console.log('[PWA Install] Install button shown');
    }
  }

  /**
   * Hide install button
   */
  hideInstallButton() {
    if (this.installContainer) {
      this.installContainer.style.display = 'none';
      console.log('[PWA Install] Install button hidden');
    }
  }

  /**
   * Dismiss install prompt
   * User clicked the close button
   */
  dismissInstallPrompt() {
    this.hideInstallButton();
    this.installAttempted = true;
    
    // Store dismissal preference
    localStorage.setItem('pwa_install_dismissed', 'true');
    
    console.log('[PWA Install] Install prompt dismissed by user');
  }

  /**
   * Handle install button click
   */
  async handleInstallClick() {
    console.log('[PWA Install] Install button clicked');

    // Check if we have a deferred prompt
    if (!this.deferredPrompt) {
      console.warn('[PWA Install] No deferred prompt available');
      return;
    }

    // Show the install prompt
    this.deferredPrompt.prompt();

    // Wait for user response
    const { outcome } = await this.deferredPrompt.userChoice;
    
    console.log(`[PWA Install] User response: ${outcome}`);

    if (outcome === 'accepted') {
      console.log('[PWA Install] User accepted installation');
      // The appinstalled event will fire after successful installation
    } else {
      console.log('[PWA Install] User dismissed installation');
      // User dismissed the prompt, but we can show it again later
    }

    // Clear the deferred prompt
    this.deferredPrompt = null;
  }

  /**
   * Show installation success message
   */
  showInstallationSuccess() {
    // Create success notification
    const notification = document.createElement('div');
    notification.className = 'alert alert-success alert-dismissible fade show pwa-install-success';
    notification.innerHTML = `
      <strong>Success!</strong> App installed successfully. You can now access it from your home screen.
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insert notification
    const pageContent = document.querySelector('.page-content');
    if (pageContent) {
      pageContent.insertBefore(notification, pageContent.firstChild);
    } else {
      document.body.insertBefore(notification, document.body.firstChild);
    }

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      const bsAlert = new bootstrap.Alert(notification);
      bsAlert.close();
    }, 5000);

    console.log('[PWA Install] Installation success notification shown');
  }

  /**
   * Check if app is already installed
   */
  checkIfInstalled() {
    // Check localStorage
    const installed = localStorage.getItem('pwa_installed') === 'true';
    
    // Check display mode
    const isStandalone = window.navigator.standalone === true || 
                        window.matchMedia('(display-mode: standalone)').matches;
    
    this.isInstalled = installed || isStandalone;
    
    console.log(`[PWA Install] App installed: ${this.isInstalled}`);
  }

  /**
   * Check display mode
   */
  checkDisplayMode() {
    const displayMode = this.getDisplayMode();
    console.log(`[PWA Install] Display mode: ${displayMode}`);
    
    if (displayMode === 'standalone' || displayMode === 'fullscreen') {
      // App is running as PWA
      this.isInstalled = true;
      localStorage.setItem('pwa_installed', 'true');
    }
  }

  /**
   * Get current display mode
   */
  getDisplayMode() {
    const isStandalone = window.navigator.standalone === true;
    if (isStandalone) {
      return 'standalone';
    }

    if (window.matchMedia('(display-mode: standalone)').matches) {
      return 'standalone';
    }

    if (window.matchMedia('(display-mode: fullscreen)').matches) {
      return 'fullscreen';
    }

    if (window.matchMedia('(display-mode: minimal-ui)').matches) {
      return 'minimal-ui';
    }

    return 'browser';
  }

  /**
   * Check if installation prompt should be shown
   */
  shouldShowPrompt() {
    // Don't show if already installed
    if (this.isInstalled) {
      return false;
    }

    // Don't show if user dismissed it
    if (localStorage.getItem('pwa_install_dismissed') === 'true') {
      return false;
    }

    // Don't show if we don't have a deferred prompt
    if (!this.deferredPrompt) {
      return false;
    }

    return true;
  }

  /**
   * Reset installation state (for testing)
   */
  reset() {
    this.deferredPrompt = null;
    this.isInstalled = false;
    this.installAttempted = false;
    localStorage.removeItem('pwa_installed');
    localStorage.removeItem('pwa_install_dismissed');
    this.hideInstallButton();
    console.log('[PWA Install] State reset');
  }
}

// Initialize PWA install prompt when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.pwaInstallPrompt = new PWAInstallPrompt();
  });
} else {
  window.pwaInstallPrompt = new PWAInstallPrompt();
}
