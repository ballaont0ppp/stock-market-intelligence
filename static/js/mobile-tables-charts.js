/**
 * Mobile Tables and Charts Optimization
 * Provides responsive table scrolling, card-based table display, and touch-optimized chart interactions
 * 
 * Features:
 * - Horizontal scrolling for tables on mobile
 * - Card-based table display as alternative
 * - Responsive chart sizing
 * - Touch-friendly interactions
 * - Loading and error states
 */

class MobileTablesCharts {
  constructor() {
    this.tables = [];
    this.charts = [];
    this.init();
  }

  /**
   * Initialize mobile tables and charts
   */
  init() {
    console.log('[Mobile Tables/Charts] Initializing...');
    
    // Initialize responsive tables
    this.initTables();
    
    // Initialize responsive charts
    this.initCharts();
    
    // Handle window resize
    window.addEventListener('resize', () => this.handleResize());
    
    console.log('[Mobile Tables/Charts] Initialized');
  }

  /**
   * Initialize responsive tables
   */
  initTables() {
    const tables = document.querySelectorAll('.table-responsive-mobile, .table-responsive, .table-responsive-wrapper');
    
    tables.forEach((table) => {
      // Add scroll indicator
      this.addScrollIndicator(table);
      
      // Make table scrollable
      this.makeTableScrollable(table);
      
      // Add touch interactions
      this.addTableTouchInteractions(table);
      
      this.tables.push(table);
    });
    
    console.log(`[Mobile Tables/Charts] Initialized ${tables.length} tables`);
  }

  /**
   * Add scroll indicator to table
   */
  addScrollIndicator(table) {
    const wrapper = table.closest('.table-wrapper') || table;
    
    // Check if table is scrollable
    if (table.scrollWidth > table.clientWidth) {
      wrapper.classList.add('scrollable');
    }
    
    // Update on scroll
    table.addEventListener('scroll', () => {
      const isScrollable = table.scrollWidth > table.clientWidth;
      const isAtEnd = table.scrollLeft + table.clientWidth >= table.scrollWidth - 10;
      
      if (isScrollable && !isAtEnd) {
        wrapper.classList.add('scrollable');
      } else {
        wrapper.classList.remove('scrollable');
      }
    });
  }

  /**
   * Make table scrollable with momentum
   */
  makeTableScrollable(table) {
    // Enable momentum scrolling on iOS
    table.style.webkitOverflowScrolling = 'touch';
    // Ensure horizontal overflow is enabled on containers
    table.style.overflowX = 'auto';
    
    // Add scroll snap for better UX
    table.style.scrollSnapType = 'x mandatory';
    table.style.scrollBehavior = 'smooth';
  }

  /**
   * Add touch interactions to table
   */
  addTableTouchInteractions(table) {
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach((row) => {
      // Add click handler
      row.addEventListener('click', (e) => {
        this.handleRowClick(row, e);
      });
      
      // Add touch feedback
      row.addEventListener('touchstart', () => {
        row.style.opacity = '0.8';
      });
      
      row.addEventListener('touchend', () => {
        row.style.opacity = '1';
      });
    });
  }

  /**
   * Handle row click
   */
  handleRowClick(row, event) {
    // Emit custom event for row click
    const clickEvent = new CustomEvent('tableRowClick', {
      detail: {
        row: row,
        data: this.extractRowData(row)
      }
    });
    
    row.dispatchEvent(clickEvent);
    console.log('[Mobile Tables/Charts] Row clicked:', this.extractRowData(row));
  }

  /**
   * Extract data from table row
   */
  extractRowData(row) {
    const cells = row.querySelectorAll('td');
    const data = {};
    
    cells.forEach((cell, index) => {
      data[`col_${index}`] = cell.textContent.trim();
    });
    
    return data;
  }

  /**
   * Initialize responsive charts
   */
  initCharts() {
    const containers = new Set();
    // Preferred explicit containers
    document.querySelectorAll('.chart-container-mobile').forEach(c => containers.add(c));

    // Fallback: find parents of canvases commonly used in cards/page content
    if (containers.size === 0) {
      document.querySelectorAll('.chart-card canvas, .card canvas, .page-content canvas').forEach((canvas) => {
        if (canvas && canvas.parentElement) {
          containers.add(canvas.parentElement);
        }
      });
    }

    containers.forEach((container) => {
      // Set responsive height
      this.setChartHeight(container);

      // Add touch interactions
      this.addChartTouchInteractions(container);

      this.charts.push(container);
    });

    console.log(`[Mobile Tables/Charts] Initialized ${containers.size} charts`);
  }

  /**
   * Set responsive chart height
   */
  setChartHeight(container) {
    const updateHeight = () => {
      const width = window.innerWidth;
      let height;
      
      if (width <= 576) {
        height = 250;
      } else if (width <= 767) {
        height = 300;
      } else {
        height = 400;
      }
      
      container.style.height = `${height}px`;
    };
    
    updateHeight();
    window.addEventListener('resize', updateHeight);
  }

  /**
   * Add touch interactions to charts
   */
  addChartTouchInteractions(container) {
    const canvas = container.querySelector('canvas');
    
    if (!canvas) return;
    
    // Prevent default touch behaviors
    canvas.addEventListener('touchstart', (e) => {
      e.preventDefault();
    }, { passive: false });
    
    // Add touch feedback
    canvas.addEventListener('touchstart', () => {
      canvas.style.opacity = '0.9';
    });
    
    canvas.addEventListener('touchend', () => {
      canvas.style.opacity = '1';
    });
  }

  /**
   * Show loading state for chart
   */
  showChartLoading(container) {
    container.innerHTML = '<div class="chart-loading">Loading chart...</div>';
  }

  /**
   * Show error state for chart
   */
  showChartError(container, message = 'Failed to load chart') {
    container.innerHTML = `<div class="chart-error">${message}</div>`;
  }

  /**
   * Handle window resize
   */
  handleResize() {
    // Update table scroll indicators
    this.tables.forEach((table) => {
      const wrapper = table.closest('.table-wrapper') || table;
      this.addScrollIndicator(table);
    });
    
    // Update chart heights
    this.charts.forEach((container) => {
      this.setChartHeight(container);
    });
  }

  /**
   * Convert table to card view (for mobile)
   */
  convertTableToCards(table) {
    const rows = table.querySelectorAll('tbody tr');
    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
    
    const cards = rows.map((row) => {
      const cells = row.querySelectorAll('td');
      const card = document.createElement('div');
      card.className = 'card';
      
      let html = '<div class="card-header">' + headers[0] + '</div><div class="card-body">';
      
      cells.forEach((cell, index) => {
        html += `
          <div class="card-row">
            <span class="card-label">${headers[index]}</span>
            <span class="card-value">${cell.textContent.trim()}</span>
          </div>
        `;
      });
      
      html += '</div>';
      card.innerHTML = html;
      
      return card;
    });
    
    return cards;
  }

  /**
   * Get table statistics
   */
  getTableStats(table) {
    const rows = table.querySelectorAll('tbody tr');
    const cells = table.querySelectorAll('tbody td');
    
    return {
      rowCount: rows.length,
      columnCount: table.querySelectorAll('thead th').length,
      cellCount: cells.length
    };
  }

  /**
   * Export table data
   */
  exportTableData(table, format = 'json') {
    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
    const rows = Array.from(table.querySelectorAll('tbody tr')).map((row) => {
      const cells = row.querySelectorAll('td');
      const rowData = {};
      
      cells.forEach((cell, index) => {
        rowData[headers[index]] = cell.textContent.trim();
      });
      
      return rowData;
    });
    
    if (format === 'json') {
      return JSON.stringify(rows, null, 2);
    } else if (format === 'csv') {
      let csv = headers.join(',') + '\n';
      rows.forEach((row) => {
        csv += Object.values(row).join(',') + '\n';
      });
      return csv;
    }
    
    return rows;
  }
}

/**
 * Initialize on DOM ready
 */
document.addEventListener('DOMContentLoaded', () => {
  window.mobileTablesCharts = new MobileTablesCharts();
});

console.log('[Mobile Tables/Charts] Script loaded');
