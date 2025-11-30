/**
 * Mobile Navigation Handler
 * Handles hamburger menu, swipe gestures, and touch interactions
 */

class MobileNavigation {
  constructor() {
    this.sidebar = document.getElementById('sidebar');
    this.sidebarOverlay = document.getElementById('sidebarOverlay');
    this.menuToggle = document.getElementById('menuToggle');
    this.touchStartX = 0;
    this.touchEndX = 0;
    this.isOpen = false;
    
    this.init();
  }

  init() {
    if (!this.sidebar || !this.menuToggle) return;
    
    // Menu toggle click handler
    this.menuToggle.addEventListener('click', () => this.toggleMenu());
    
    // Close button click handler
    const closeBtn = document.getElementById('sidebarCloseBtn');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.closeMenu());
    }
    
    // Overlay click handler
    if (this.sidebarOverlay) {
      this.sidebarOverlay.addEventListener('click', () => this.closeMenu());
    }
    
    // Swipe gesture handlers
    document.addEventListener('touchstart', (e) => this.handleTouchStart(e), false);
    document.addEventListener('touchend', (e) => this.handleTouchEnd(e), false);
    
    // Close menu when clicking on a navigation item
    this.setupNavItemClickHandlers();
    
    // Keyboard support (ESC to close)
    document.addEventListener('keydown', (e) => this.handleKeydown(e));
    
    // Handle window resize
    window.addEventListener('resize', () => this.handleResize());
  }

  /**
   * Toggle menu open/close
   */
  toggleMenu() {
    if (this.isOpen) {
      this.closeMenu();
    } else {
      this.openMenu();
    }
  }

  /**
   * Open the sidebar menu
   */
  openMenu() {
    if (!this.sidebar) return;
    
    this.sidebar.classList.add('open');
    if (this.sidebarOverlay) {
      this.sidebarOverlay.classList.add('open');
    }
    this.isOpen = true;
    
    // Prevent body scroll when menu is open
    document.body.style.overflow = 'hidden';
    
    // Trigger animation
    this.sidebar.style.transform = 'translateX(0)';
  }

  /**
   * Close the sidebar menu
   */
  closeMenu() {
    if (!this.sidebar) return;
    
    this.sidebar.classList.remove('open');
    if (this.sidebarOverlay) {
      this.sidebarOverlay.classList.remove('open');
    }
    this.isOpen = false;
    
    // Restore body scroll
    document.body.style.overflow = '';
    
    // Trigger animation
    this.sidebar.style.transform = 'translateX(-100%)';
  }

  /**
   * Handle touch start for swipe detection
   */
  handleTouchStart(e) {
    this.touchStartX = e.changedTouches[0].screenX;
  }

  /**
   * Handle touch end for swipe detection
   */
  handleTouchEnd(e) {
    this.touchEndX = e.changedTouches[0].screenX;
    this.handleSwipe();
  }

  /**
   * Detect and handle swipe gestures
   */
  handleSwipe() {
    const swipeThreshold = 50; // Minimum distance for swipe
    const diff = this.touchStartX - this.touchEndX;
    
    // Swipe left (close menu)
    if (diff > swipeThreshold && this.isOpen) {
      this.closeMenu();
    }
    
    // Swipe right (open menu) - only if starting from left edge
    if (diff < -swipeThreshold && !this.isOpen && this.touchStartX < 50) {
      this.openMenu();
    }
  }

  /**
   * Setup click handlers for navigation items
   */
  setupNavItemClickHandlers() {
    const navItems = document.querySelectorAll('.sidebar-nav-item');
    navItems.forEach(item => {
      item.addEventListener('click', () => {
        // Close menu after clicking a nav item
        setTimeout(() => this.closeMenu(), 100);
      });
    });
  }

  /**
   * Handle keyboard events
   */
  handleKeydown(e) {
    // ESC key to close menu
    if (e.key === 'Escape' && this.isOpen) {
      this.closeMenu();
    }
  }

  /**
   * Handle window resize
   */
  handleResize() {
    // Close menu on larger screens
    if (window.innerWidth > 767 && this.isOpen) {
      this.closeMenu();
    }
  }

  /**
   * Check if menu is currently open
   */
  isMenuOpen() {
    return this.isOpen;
  }
}

// Initialize mobile navigation when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.mobileNav = new MobileNavigation();
});
