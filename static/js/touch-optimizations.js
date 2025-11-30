/**
 * Touch Optimizations for Mobile PWA
 * Implements smooth scrolling, momentum scrolling, and touch event handling
 * 
 * Features:
 * - CSS smooth scrolling with momentum
 * - Touch event optimization
 * - Loading states for perceived performance
 * - Scroll position restoration
 * - Touch feedback animations
 */

class TouchOptimizations {
  constructor() {
    this.touchStartX = 0;
    this.touchStartY = 0;
    this.touchEndX = 0;
    this.touchEndY = 0;
    this.isScrolling = false;
    this.scrollTimeout = null;
    
    this.init();
  }

  /**
   * Initialize touch optimizations
   */
  init() {
    // Enable smooth scrolling via CSS
    this.enableSmoothScrolling();
    
    // Add touch event listeners
    this.attachTouchListeners();
    
    // Add scroll event listeners
    this.attachScrollListeners();
    
    // Add loading state handlers
    this.attachLoadingStateHandlers();
    
    // Restore scroll position on page load
    this.restoreScrollPosition();
    
    console.log('[Touch Optimizations] Initialized');
  }

  /**
   * Enable smooth scrolling via CSS
   */
  enableSmoothScrolling() {
    // Check if smooth scrolling is already enabled
    if (document.documentElement.style.scrollBehavior === 'smooth') {
      return;
    }

    // Set smooth scrolling on html element
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add momentum scrolling for iOS
    const scrollableElements = document.querySelectorAll(
      '.sidebar, .main-content, .page-content, [class*="scroll"]'
    );
    
    scrollableElements.forEach((element) => {
      // Enable momentum scrolling on iOS
      element.style.webkitOverflowScrolling = 'touch';
    });

    console.log('[Touch Optimizations] Smooth scrolling enabled');
  }

  /**
   * Attach touch event listeners
   */
  attachTouchListeners() {
    document.addEventListener('touchstart', (e) => this.handleTouchStart(e), false);
    document.addEventListener('touchend', (e) => this.handleTouchEnd(e), false);
    document.addEventListener('touchmove', (e) => this.handleTouchMove(e), false);
    
    console.log('[Touch Optimizations] Touch listeners attached');
  }

  /**
   * Handle touch start event
   */
  handleTouchStart(e) {
    this.touchStartX = e.changedTouches[0].screenX;
    this.touchStartY = e.changedTouches[0].screenY;
  }

  /**
   * Handle touch end event
   */
  handleTouchEnd(e) {
    this.touchEndX = e.changedTouches[0].screenX;
    this.touchEndY = e.changedTouches[0].screenY;
    
    // Detect swipe gestures
    this.detectSwipe();
  }

  /**
   * Handle touch move event
   */
  handleTouchMove(e) {
    // Add visual feedback during scrolling
    const target = e.target;
    
    // Add scrolling class for visual feedback
    if (!target.classList.contains('scrolling')) {
      target.classList.add('scrolling');
    }
  }

  /**
   * Detect swipe gestures
   */
  detectSwipe() {
    const swipeThreshold = 50; // Minimum distance for swipe
    const diffX = this.touchStartX - this.touchEndX;
    const diffY = this.touchStartY - this.touchEndY;

    // Determine if it's a horizontal or vertical swipe
    if (Math.abs(diffX) > Math.abs(diffY)) {
      // Horizontal swipe
      if (Math.abs(diffX) > swipeThreshold) {
        if (diffX > 0) {
          // Swiped left
          this.handleSwipeLeft();
        } else {
          // Swiped right
          this.handleSwipeRight();
        }
      }
    }
  }

  /**
   * Handle swipe left
   */
  handleSwipeLeft() {
    console.log('[Touch Optimizations] Swipe left detected');
    // Could be used for navigation or other actions
  }

  /**
   * Handle swipe right
   */
  handleSwipeRight() {
    console.log('[Touch Optimizations] Swipe right detected');
    // Could be used for navigation or other actions
  }

  /**
   * Attach scroll event listeners
   */
  attachScrollListeners() {
    window.addEventListener('scroll', () => this.handleScroll(), { passive: true });
    
    console.log('[Touch Optimizations] Scroll listeners attached');
  }

  /**
   * Handle scroll event
   */
  handleScroll() {
    // Mark as scrolling
    this.isScrolling = true;
    
    // Save scroll position
    this.saveScrollPosition();
    
    // Clear existing timeout
    if (this.scrollTimeout) {
      clearTimeout(this.scrollTimeout);
    }

    // Set timeout to detect when scrolling stops
    this.scrollTimeout = setTimeout(() => {
      this.isScrolling = false;
      console.log('[Touch Optimizations] Scroll ended');
    }, 150);
  }

  /**
   * Save scroll position to sessionStorage
   */
  saveScrollPosition() {
    const scrollPosition = {
      x: window.scrollX,
      y: window.scrollY,
      timestamp: Date.now()
    };
    
    try {
      sessionStorage.setItem('scrollPosition', JSON.stringify(scrollPosition));
    } catch (e) {
      console.warn('[Touch Optimizations] Could not save scroll position:', e);
    }
  }

  /**
   * Restore scroll position from sessionStorage
   */
  restoreScrollPosition() {
    try {
      const saved = sessionStorage.getItem('scrollPosition');
      if (saved) {
        const scrollPosition = JSON.parse(saved);
        
        // Only restore if saved recently (within 5 minutes)
        const timeDiff = Date.now() - scrollPosition.timestamp;
        if (timeDiff < 5 * 60 * 1000) {
          window.scrollTo(scrollPosition.x, scrollPosition.y);
          console.log('[Touch Optimizations] Scroll position restored');
        }
      }
    } catch (e) {
      console.warn('[Touch Optimizations] Could not restore scroll position:', e);
    }
  }

  /**
   * Attach loading state handlers
   */
  attachLoadingStateHandlers() {
    // Show loading state on form submission
    document.addEventListener('submit', (e) => {
      const form = e.target;
      const submitButton = form.querySelector('button[type="submit"]');
      
      if (submitButton) {
        this.showLoadingState(submitButton);
      }
    });

    // Show loading state on link click
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a');
      
      if (link && !link.hasAttribute('data-no-loading') && link.href) {
        // Check if it's an internal link
        if (link.hostname === window.location.hostname) {
          this.showLoadingState(link);
        }
      }
    });

    console.log('[Touch Optimizations] Loading state handlers attached');
  }

  /**
   * Show loading state on element
   */
  showLoadingState(element) {
    // Add loading class
    element.classList.add('loading');
    
    // Disable element
    element.disabled = true;
    
    // Store original content
    const originalContent = element.innerHTML;
    
    // Show loading spinner
    element.innerHTML = `
      <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
      <span>Loading...</span>
    `;

    // Restore after timeout (in case page doesn't load)
    setTimeout(() => {
      element.classList.remove('loading');
      element.disabled = false;
      element.innerHTML = originalContent;
    }, 5000);
  }

  /**
   * Scroll to element smoothly
   */
  scrollToElement(element, offset = 0) {
    if (!element) return;

    const elementPosition = element.getBoundingClientRect().top + window.scrollY;
    const offsetPosition = elementPosition - offset;

    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    });

    console.log('[Touch Optimizations] Scrolled to element');
  }

  /**
   * Scroll to top smoothly
   */
  scrollToTop() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });

    console.log('[Touch Optimizations] Scrolled to top');
  }

  /**
   * Check if element is in viewport
   */
  isElementInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
  }

  /**
   * Add scroll-to-top button
   */
  addScrollToTopButton() {
    // Check if button already exists
    if (document.getElementById('scroll-to-top-btn')) {
      return;
    }

    // Create button
    const button = document.createElement('button');
    button.id = 'scroll-to-top-btn';
    button.className = 'btn btn-primary scroll-to-top-btn';
    button.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="18 15 12 9 6 15"></polyline>
      </svg>
    `;
    button.title = 'Scroll to top';
    button.style.display = 'none';

    // Add click handler
    button.addEventListener('click', () => this.scrollToTop());

    // Add to page
    document.body.appendChild(button);

    // Show/hide button based on scroll position
    window.addEventListener('scroll', () => {
      if (window.scrollY > 300) {
        button.style.display = 'flex';
      } else {
        button.style.display = 'none';
      }
    }, { passive: true });

    console.log('[Touch Optimizations] Scroll-to-top button added');
  }

  /**
   * Optimize touch feedback
   */
  optimizeTouchFeedback() {
    // Add touch feedback to interactive elements
    const interactiveElements = document.querySelectorAll(
      'button, a, input, select, textarea, [role="button"]'
    );

    interactiveElements.forEach((element) => {
      // Add active state on touch
      element.addEventListener('touchstart', () => {
        element.classList.add('touch-active');
      });

      element.addEventListener('touchend', () => {
        element.classList.remove('touch-active');
      });

      element.addEventListener('touchcancel', () => {
        element.classList.remove('touch-active');
      });
    });

    console.log('[Touch Optimizations] Touch feedback optimized');
  }

  /**
   * Disable double-tap zoom on buttons
   */
  disableDoubleTapZoom() {
    let lastTouchEnd = 0;

    document.addEventListener('touchend', (e) => {
      const now = Date.now();
      if (now - lastTouchEnd <= 300) {
        e.preventDefault();
      }
      lastTouchEnd = now;
    }, false);

    console.log('[Touch Optimizations] Double-tap zoom disabled');
  }

  /**
   * Get scroll position
   */
  getScrollPosition() {
    return {
      x: window.scrollX,
      y: window.scrollY
    };
  }

  /**
   * Set scroll position
   */
  setScrollPosition(x, y) {
    window.scrollTo(x, y);
  }
}

// Initialize touch optimizations when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.touchOptimizations = new TouchOptimizations();
    
    // Add scroll-to-top button
    window.touchOptimizations.addScrollToTopButton();
    
    // Optimize touch feedback
    window.touchOptimizations.optimizeTouchFeedback();
  });
} else {
  window.touchOptimizations = new TouchOptimizations();
  
  // Add scroll-to-top button
  window.touchOptimizations.addScrollToTopButton();
  
  // Optimize touch feedback
  window.touchOptimizations.optimizeTouchFeedback();
}
