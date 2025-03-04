document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchForm = document.getElementById('searchForm');
    const searchResults = document.getElementById('searchResults');
    const loadingSpinner = document.querySelector('.loading-spinner');

    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(searchForm);
            const searchParams = new URLSearchParams(formData);
            
            loadingSpinner.style.display = 'block';
            searchResults.style.opacity = '0.5';

            fetch(`/search?${searchParams.toString()}`)
                .then(response => response.json())
                .then(tools => {
                    searchResults.innerHTML = '';
                    tools.forEach(tool => {
                        const toolCard = createToolCard(tool);
                        searchResults.appendChild(toolCard);
                    });
                })
                .catch(error => {
                    console.error('Search error:', error);
                    searchResults.innerHTML = '<div class="alert alert-error">Search failed. Please try again.</div>';
                })
                .finally(() => {
                    loadingSpinner.style.display = 'none';
                    searchResults.style.opacity = '1';
                });
        });
    }

    // Tool card creation
    function createToolCard(tool) {
        const card = document.createElement('div');
        card.className = 'card mb-3';
        card.innerHTML = `
            <div class="card-body">
                <h5 class="card-title">${escapeHtml(tool.name)}</h5>
                <h6 class="card-subtitle mb-2 text-muted">${escapeHtml(tool.developer)}</h6>
                <span class="category-badge">${escapeHtml(tool.category)}</span>
                <p class="card-text mt-2">${escapeHtml(tool.description)}</p>
                <div class="tags">
                    ${tool.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
                </div>
                <div class="mt-3">
                    <a href="${tool.url}" class="btn btn-primary btn-sm" target="_blank">Visit Tool</a>
                    <a href="/tool/${tool.id}" class="btn btn-secondary btn-sm">Details</a>
                </div>
            </div>
        `;
        return card;
    }

    // HTML escape function
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Flash message auto-hide
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        }, 3000);
    });

    // Tool comparison functionality
    const compareCheckboxes = document.querySelectorAll('.compare-checkbox');
    const compareButton = document.getElementById('compareButton');

    if (compareCheckboxes.length && compareButton) {
        compareCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateCompareButton);
        });

        function updateCompareButton() {
            const selectedTools = Array.from(compareCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);

            compareButton.disabled = selectedTools.length < 2;
            compareButton.href = `/compare?${selectedTools.map(id => `tools=${id}`).join('&')}`;
        }
    }
});
