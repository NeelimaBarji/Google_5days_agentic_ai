// State management
let releases = [];
let filteredReleases = [];
let currentFilterType = 'all';
let currentSearchQuery = '';
let currentSortOrder = 'newest';
let selectedReleases = new Map(); // Track selection by ID

// Elements
const refreshBtn = document.getElementById('refresh-button');
const spinnerIcon = refreshBtn.querySelector('.spinner-icon');
const lastUpdatedText = document.getElementById('last-updated-text');
const searchInput = document.getElementById('search-input');
const clearSearchBtn = document.getElementById('clear-search-btn');
const filterChipsContainer = document.getElementById('filter-chips');
const sortSelect = document.getElementById('sort-select');
const resultsInfo = document.getElementById('search-results-info');
const matchingCount = document.getElementById('matching-count');

// State Containers
const loadingState = document.getElementById('loading-state');
const errorState = document.getElementById('error-state');
const errorMessage = document.getElementById('error-message');
const emptyState = document.getElementById('empty-state');
const releasesGrid = document.getElementById('releases-grid');
const retryBtn = document.getElementById('retry-btn');
const resetFiltersBtn = document.getElementById('reset-filters-btn');

// Modal Elements
const tweetModal = document.getElementById('tweet-modal');
const tweetTextarea = document.getElementById('tweet-textarea');
const charCounter = document.getElementById('char-counter');
const charProgress = document.getElementById('char-progress');
const copyTextBtn = document.getElementById('copy-text-btn');
const copyBtnText = document.getElementById('copy-btn-text');
const postTweetBtn = document.getElementById('post-tweet-btn');
const closeModalBtn = document.getElementById('close-modal-btn');

// Selection Bar Elements
const floatingBar = document.getElementById('floating-action-bar');
const selectedCount = document.getElementById('selected-count');
const clearSelectionBtn = document.getElementById('clear-selection-btn');
const tweetSelectedBtn = document.getElementById('tweet-selected-btn');

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    fetchReleases();
    setupEventListeners();
});

// --- Event Listeners Setup ---
function setupEventListeners() {
    // Refresh button
    refreshBtn.addEventListener('click', () => fetchReleases(true));
    retryBtn.addEventListener('click', () => fetchReleases(true));

    // Search input
    searchInput.addEventListener('input', (e) => {
        currentSearchQuery = e.target.value.trim().toLowerCase();
        toggleClearSearchButton();
        applyFilters();
    });

    // Clear search
    clearSearchBtn.addEventListener('click', () => {
        searchInput.value = '';
        currentSearchQuery = '';
        toggleClearSearchButton();
        applyFilters();
    });

    // Filter Chips
    filterChipsContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('chip')) {
            // Update active state
            filterChipsContainer.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
            e.target.classList.add('active');

            // Apply filter
            currentFilterType = e.target.getAttribute('data-type');
            applyFilters();
        }
    });

    // Sort select
    sortSelect.addEventListener('change', (e) => {
        currentSortOrder = e.target.value;
        applyFilters();
    });

    // Reset Filters button (on empty state)
    resetFiltersBtn.addEventListener('click', () => {
        searchInput.value = '';
        currentSearchQuery = '';
        toggleClearSearchButton();
        
        filterChipsContainer.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        filterChipsContainer.querySelector('[data-type="all"]').classList.add('active');
        currentFilterType = 'all';
        
        applyFilters();
    });

    // Modal Close
    closeModalBtn.addEventListener('click', closeTweetModal);
    tweetModal.addEventListener('click', (e) => {
        if (e.target === tweetModal) closeTweetModal();
    });

    // Real-time Tweet character tracking
    tweetTextarea.addEventListener('input', updateCharCountProgress);

    // Share and Copy in Modal
    copyTextBtn.addEventListener('click', copyTweetToClipboard);
    postTweetBtn.addEventListener('click', executeTweet);

    // Selection Bar actions
    clearSelectionBtn.addEventListener('click', clearSelection);
    tweetSelectedBtn.addEventListener('click', () => {
        if (selectedReleases.size > 0) {
            openTweetModal(Array.from(selectedReleases.values()));
        }
    });
}

// --- Fetch Data ---
async function fetchReleases(forceRefresh = false) {
    showLoading();
    
    // Toggle active spinner class
    spinnerIcon.classList.add('spinning');
    refreshBtn.disabled = true;

    const url = forceRefresh ? '/api/releases?refresh=true' : '/api/releases';

    try {
        const response = await fetch(url);
        const result = await response.json();

        if (response.ok && result.success) {
            releases = result.data;
            
            // Clean up selections that no longer exist in retrieved data
            const validIds = new Set(releases.map(r => r.id));
            for (let id of selectedReleases.keys()) {
                if (!validIds.has(id)) {
                    selectedReleases.delete(id);
                }
            }
            updateFloatingBar();
            
            lastUpdatedText.textContent = `Last sync: ${result.last_updated}`;
            applyFilters();
        } else {
            showError(result.error || 'Server error occurred');
        }
    } catch (err) {
        showError('Network connectivity error. Could not reach Flask server.');
    } finally {
        spinnerIcon.classList.remove('spinning');
        refreshBtn.disabled = false;
    }
}

// --- Apply Filters, Search & Sort ---
function applyFilters() {
    // 1. Filter by Type
    filteredReleases = releases.filter(item => {
        const matchType = currentFilterType === 'all' || item.type === currentFilterType;
        
        // 2. Search query matching
        const matchSearch = currentSearchQuery === '' || 
            item.content_text.toLowerCase().includes(currentSearchQuery) || 
            item.type.toLowerCase().includes(currentSearchQuery) ||
            item.date.toLowerCase().includes(currentSearchQuery);

        return matchType && matchSearch;
    });

    // 3. Sort Results
    filteredReleases.sort((a, b) => {
        const dateA = new Date(a.updated_iso);
        const dateB = new Date(b.updated_iso);
        
        if (currentSortOrder === 'newest') {
            return dateB - dateA;
        } else {
            return dateA - dateB;
        }
    });

    // Update results meta and render
    updateResultsMeta();
    renderReleases();
}

// --- Render Timeline Grid ---
function renderReleases() {
    releasesGrid.innerHTML = '';

    if (filteredReleases.length === 0) {
        showEmpty();
        return;
    }

    showGrid();

    filteredReleases.forEach((item, index) => {
        const isSelected = selectedReleases.has(item.id);
        const card = document.createElement('article');
        card.className = `release-card type-${item.type.toLowerCase()} fade-in-entry${isSelected ? ' selected' : ''}`;
        card.style.animationDelay = `${Math.min(index * 0.05, 0.5)}s`;
        
        // Create custom badge type class
        let badgeClass = 'badge-general';
        if (item.type.toLowerCase() === 'feature') badgeClass = 'badge-feature';
        else if (item.type.toLowerCase() === 'announcement') badgeClass = 'badge-announcement';
        else if (item.type.toLowerCase() === 'issue') badgeClass = 'badge-issue';
        else if (item.type.toLowerCase() === 'deprecation') badgeClass = 'badge-deprecation';

        // Render card content with custom select checkbox
        card.innerHTML = `
            <div class="card-header">
                <div class="header-left">
                    <label class="custom-checkbox" title="Select update to share">
                        <input type="checkbox" class="card-select-checkbox" data-id="${item.id}" ${isSelected ? 'checked' : ''}>
                        <span class="checkbox-checkmark"></span>
                    </label>
                    <span class="date-badge">
                        <!-- Calendar SVG Icon -->
                        <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
                            <path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zm0-12H5V6h14v2zm-7 5h5v5h-5z"/>
                        </svg>
                        <span>${item.date}</span>
                    </span>
                </div>
                <span class="badge ${badgeClass}">${item.type}</span>
            </div>
            
            <div class="card-body">
                ${item.content_html}
            </div>
            
            <div class="card-footer">
                <a href="${item.link}" target="_blank" rel="noopener noreferrer" class="doc-link">
                    <span>Docs Link</span>
                    <svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor">
                        <path d="M19 19H5V5h7V3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2v-7h-2v7zM14 3v2h3.59l-9.83 9.83 1.41 1.41L19 6.41V10h2V3h-7z"/>
                    </svg>
                </a>
                
                <div class="footer-actions">
                    <button class="btn btn-card btn-card-copy" title="Copy text to clipboard">
                        Copy Text
                    </button>
                    <button class="btn btn-card btn-card-tweet">
                        <!-- Custom Tweet/X icon -->
                        <svg viewBox="0 0 24 24" width="12" height="12" fill="currentColor">
                            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                        </svg>
                        <span>Tweet</span>
                    </button>
                </div>
            </div>
        `;

        // Event hooks
        const copyBtn = card.querySelector('.btn-card-copy');
        copyBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            navigator.clipboard.writeText(item.content_text).then(() => {
                copyBtn.textContent = 'Copied!';
                copyBtn.style.color = '#10B981';
                setTimeout(() => {
                    copyBtn.textContent = 'Copy Text';
                    copyBtn.style.color = '';
                }, 2000);
            });
        });

        const tweetBtn = card.querySelector('.btn-card-tweet');
        tweetBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            openTweetModal([item]);
        });

        // Click anywhere on card to toggle selection (ignoring interactive elements)
        card.addEventListener('click', (e) => {
            if (e.target.closest('a') || e.target.closest('button') || e.target.closest('.custom-checkbox')) {
                return;
            }
            const checkbox = card.querySelector('.card-select-checkbox');
            checkbox.checked = !checkbox.checked;
            checkbox.dispatchEvent(new Event('change'));
        });

        // Checkbox change listener
        const checkbox = card.querySelector('.card-select-checkbox');
        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                card.classList.add('selected');
                selectedReleases.set(item.id, item);
            } else {
                card.classList.remove('selected');
                selectedReleases.delete(item.id);
            }
            updateFloatingBar();
        });

        releasesGrid.appendChild(card);
    });
}

// --- Selection State Helpers ---
function updateFloatingBar() {
    if (selectedReleases.size > 0) {
        selectedCount.textContent = selectedReleases.size;
        floatingBar.classList.add('active');
    } else {
        floatingBar.classList.remove('active');
    }
}

function clearSelection() {
    selectedReleases.clear();
    updateFloatingBar();
    
    // Update UI elements
    releasesGrid.querySelectorAll('.release-card').forEach(card => {
        card.classList.remove('selected');
        const checkbox = card.querySelector('.card-select-checkbox');
        if (checkbox) checkbox.checked = false;
    });
}

// --- Dynamic Tweet Formatter ---
function openTweetModal(selectedItems) {
    if (!selectedItems || selectedItems.length === 0) return;
    
    let compiledText = '';
    
    if (selectedItems.length === 1) {
        // Single update formatting
        const item = selectedItems[0];
        const prefix = `BigQuery ${item.type} (${item.date}): `;
        const suffix = ` #BigQuery #GoogleCloud`;
        const urlLength = 23;
        const docLinkText = `\n\nRead more: ${item.link}`;
        const staticLength = prefix.length + suffix.length + `\n\nRead more: `.length + urlLength;
        const maxDescLength = 280 - staticLength;

        let desc = item.content_text;
        if (desc.length > maxDescLength) {
            desc = desc.substring(0, maxDescLength - 3) + '...';
        }

        compiledText = `${prefix}${desc}${docLinkText}${suffix}`;
    } else {
        // Multi-update formatting
        const prefix = `BigQuery Updates:\n`;
        const link = `https://docs.cloud.google.com/bigquery/docs/release-notes`;
        const suffix = `\n\nRead more: ${link} #BigQuery #GoogleCloud`;
        
        // Convert to mutable objects for iterative truncation
        const items = selectedItems.map(item => {
            const shortDate = item.date.replace('January', 'Jan')
                                      .replace('February', 'Feb')
                                      .replace('March', 'Mar')
                                      .replace('April', 'Apr')
                                      .replace('June', 'Jun')
                                      .replace('July', 'Jul')
                                      .replace('August', 'Aug')
                                      .replace('September', 'Sep')
                                      .replace('October', 'Oct')
                                      .replace('November', 'Nov')
                                      .replace('December', 'Dec');
            return {
                meta: `• ${item.type} (${shortDate}): `,
                desc: item.content_text,
                currentDesc: item.content_text
            };
        });

        // Helper to calculate total length dynamically (URL counts as 23)
        const calcTotalLength = () => {
            let len = prefix.length;
            items.forEach(it => {
                len += it.meta.length + it.currentDesc.length + 1; // +1 for newline
            });
            len += `\n\nRead more: `.length + 23 + ` #BigQuery #GoogleCloud`.length;
            return len;
        };

        // Iteratively truncate the longest descriptions until they fit within 280 characters
        let iterations = 0;
        while (calcTotalLength() > 280 && iterations < 500) {
            iterations++;
            let longestItem = null;
            items.forEach(it => {
                if (!longestItem || it.currentDesc.length > longestItem.currentDesc.length) {
                    longestItem = it;
                }
            });

            if (!longestItem || longestItem.currentDesc.length <= 10) {
                break;
            }

            const newLen = Math.max(longestItem.currentDesc.length - 5, 10);
            longestItem.currentDesc = longestItem.desc.substring(0, newLen) + '...';
        }

        // Assemble final text
        compiledText = prefix;
        items.forEach(it => {
            compiledText += `${it.meta}${it.currentDesc}\n`;
        });
        compiledText += `\nRead more: ${link} #BigQuery #GoogleCloud`;
    }
    
    tweetTextarea.value = compiledText;
    updateCharCountProgress();
    
    tweetModal.classList.add('active');
    tweetTextarea.focus();
}

function closeTweetModal() {
    tweetModal.classList.remove('active');
}

// --- Twitter-specific URL Character Counting ---
function getTwitterLength(str) {
    // Match URLs starting with http:// or https://
    const urlRegex = /https?:\/\/[^\s]+/g;
    const urls = str.match(urlRegex) || [];
    
    let length = str.length;
    urls.forEach(url => {
        // Twitter replaces all URLs with a t.co link (23 chars)
        length = length - url.length + 23;
    });
    
    return length;
}

function updateCharCountProgress() {
    const text = tweetTextarea.value;
    const twLength = getTwitterLength(text);
    
    charCounter.textContent = `${twLength} / 280`;
    
    // Calculate percentage width (cap at 100%)
    const pct = Math.min((twLength / 280) * 100, 100);
    charProgress.style.width = `${pct}%`;

    // Colors mapping
    charProgress.className = 'progress-bar-fill';
    charCounter.className = 'char-counter';
    
    if (twLength > 280) {
        charProgress.classList.add('danger');
        charCounter.classList.add('danger');
        postTweetBtn.disabled = true;
        postTweetBtn.style.opacity = '0.5';
        postTweetBtn.style.cursor = 'not-allowed';
    } else if (twLength > 250) {
        charProgress.classList.add('warning');
        charCounter.classList.add('warning');
        postTweetBtn.disabled = false;
        postTweetBtn.style.opacity = '';
        postTweetBtn.style.cursor = '';
    } else {
        postTweetBtn.disabled = false;
        postTweetBtn.style.opacity = '';
        postTweetBtn.style.cursor = '';
    }
}

// --- Modal Share and Copy Actions ---
function copyTweetToClipboard() {
    const text = tweetTextarea.value;
    navigator.clipboard.writeText(text).then(() => {
        copyBtnText.textContent = 'Copied!';
        setTimeout(() => {
            copyBtnText.textContent = 'Copy Text';
        }, 2000);
    });
}

function executeTweet() {
    const text = tweetTextarea.value;
    const twLength = getTwitterLength(text);
    
    if (twLength > 280) return; // safety check
    
    const intentUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`;
    window.open(intentUrl, '_blank', 'noopener,noreferrer');
    closeTweetModal();
}

// --- UI Utilities ---
function toggleClearSearchButton() {
    if (searchInput.value) {
        clearSearchBtn.style.display = 'block';
    } else {
        clearSearchBtn.style.display = 'none';
    }
}

function updateResultsMeta() {
    if (currentSearchQuery !== '' || currentFilterType !== 'all') {
        resultsInfo.style.display = 'block';
        matchingCount.textContent = filteredReleases.length;
    } else {
        resultsInfo.style.display = 'none';
    }
}

function showLoading() {
    loadingState.classList.remove('hidden');
    errorState.classList.add('hidden');
    emptyState.classList.add('hidden');
    releasesGrid.classList.add('hidden');
}

function showError(msg) {
    loadingState.classList.add('hidden');
    errorState.classList.remove('hidden');
    emptyState.classList.add('hidden');
    releasesGrid.classList.add('hidden');
    errorMessage.textContent = msg;
}

function showEmpty() {
    loadingState.classList.add('hidden');
    errorState.classList.add('hidden');
    emptyState.classList.remove('hidden');
    releasesGrid.classList.add('hidden');
}

function showGrid() {
    loadingState.classList.add('hidden');
    errorState.classList.add('hidden');
    emptyState.classList.add('hidden');
    releasesGrid.classList.remove('hidden');
}
