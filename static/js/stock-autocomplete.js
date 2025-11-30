/**
 * Stock Symbol Autocomplete
 * Provides autocomplete functionality for stock symbol inputs
 */

class StockAutocomplete {
    constructor(inputElement, options = {}) {
        this.input = inputElement;
        this.options = {
            minChars: 1,
            debounceMs: 300,
            maxResults: 10,
            onSelect: null,
            ...options
        };
        
        this.resultsContainer = null;
        this.debounceTimer = null;
        this.currentFocus = -1;
        
        this.init();
    }
    
    init() {
        // Create results container
        this.resultsContainer = document.createElement('div');
        this.resultsContainer.className = 'autocomplete-results';
        this.resultsContainer.style.display = 'none';
        this.input.parentNode.style.position = 'relative';
        this.input.parentNode.appendChild(this.resultsContainer);
        
        // Attach event listeners
        this.input.addEventListener('input', (e) => this.handleInput(e));
        this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.input.addEventListener('blur', () => {
            // Delay to allow click on results
            setTimeout(() => this.hideResults(), 200);
        });
        
        // Close on click outside
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.resultsContainer.contains(e.target)) {
                this.hideResults();
            }
        });
    }
    
    handleInput(e) {
        const value = e.target.value.trim();
        
        // Clear previous timer
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }
        
        // Check minimum characters
        if (value.length < this.options.minChars) {
            this.hideResults();
            return;
        }
        
        // Debounce the search
        this.debounceTimer = setTimeout(() => {
            this.search(value);
        }, this.options.debounceMs);
    }
    
    async search(query) {
        try {
            const response = await fetch(`/api/stocks/autocomplete?q=${encodeURIComponent(query)}&limit=${this.options.maxResults}`);
            const data = await response.json();
            
            if (data.success && data.data.length > 0) {
                this.showResults(data.data);
            } else {
                this.hideResults();
            }
        } catch (error) {
            console.error('Autocomplete search error:', error);
            this.hideResults();
        }
    }
    
    showResults(results) {
        this.resultsContainer.innerHTML = '';
        this.currentFocus = -1;
        
        results.forEach((result, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.innerHTML = `
                <strong>${result.symbol}</strong>
                <span class="text-muted">${result.company_name}</span>
            `;
            
            item.addEventListener('click', () => {
                this.selectResult(result);
            });
            
            this.resultsContainer.appendChild(item);
        });
        
        this.resultsContainer.style.display = 'block';
    }
    
    hideResults() {
        this.resultsContainer.style.display = 'none';
        this.currentFocus = -1;
    }
    
    selectResult(result) {
        this.input.value = result.symbol;
        this.hideResults();
        
        // Trigger change event
        this.input.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Call custom callback if provided
        if (this.options.onSelect) {
            this.options.onSelect(result);
        }
    }
    
    handleKeydown(e) {
        const items = this.resultsContainer.querySelectorAll('.autocomplete-item');
        
        if (items.length === 0) return;
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.currentFocus++;
            if (this.currentFocus >= items.length) this.currentFocus = 0;
            this.setActive(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.currentFocus--;
            if (this.currentFocus < 0) this.currentFocus = items.length - 1;
            this.setActive(items);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (this.currentFocus > -1 && items[this.currentFocus]) {
                items[this.currentFocus].click();
            }
        } else if (e.key === 'Escape') {
            this.hideResults();
        }
    }
    
    setActive(items) {
        items.forEach((item, index) => {
            if (index === this.currentFocus) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
}

// Initialize autocomplete on page load
document.addEventListener('DOMContentLoaded', function() {
    // Find all inputs with data-autocomplete="stock"
    const stockInputs = document.querySelectorAll('input[data-autocomplete="stock"]');
    
    stockInputs.forEach(input => {
        new StockAutocomplete(input, {
            onSelect: (result) => {
                // Trigger price preview if available
                const event = new CustomEvent('stockSelected', { 
                    detail: result,
                    bubbles: true 
                });
                input.dispatchEvent(event);
            }
        });
    });
});

