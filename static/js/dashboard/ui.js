
// Functions for rendering UI components like cards and lists

export function renderSummaryCards(summary) {
    document.getElementById('total-assets-summary').textContent = summary.totalAssets;
    document.getElementById('normal-assets-summary').textContent = summary.normalAssets;
    document.getElementById('anomaly-assets-summary').textContent = summary.anomalyAssets;
}

export function renderAnomalyFeed(anomalies) {
    const feedList = document.getElementById('anomaly-feed-list');
    if (!feedList) return;

    // Clear existing content
    feedList.innerHTML = '';

    if (anomalies.length === 0) {
        feedList.innerHTML = '<div class="p-3 text-center text-muted">최신 이상 징후가 없습니다.</div>';
        return;
    }

    anomalies.forEach(anomaly => {
        const item = document.createElement('div');
        item.className = 'anomaly-feed-item';

        let iconClass = 'fas fa-check-circle';
        let iconColorClass = 'normal';
        if (anomaly.severity === 'warning') {
            iconClass = 'fas fa-exclamation-circle';
            iconColorClass = 'warning';
        } else if (anomaly.severity === 'anomaly') {
            iconClass = 'fas fa-times-circle';
            iconColorClass = 'anomaly';
        }

        item.innerHTML = `
            <div class="icon ${iconColorClass}">
                <i class="${iconClass}"></i>
            </div>
            <div class="flex-grow-1">
                <div><strong>${anomaly.assetName}</strong>: ${anomaly.type}</div>
                <div class="timestamp">${anomaly.timestamp}</div>
            </div>
        `;
        feedList.appendChild(item);
    });
}

export function renderAssetList(assets) {
    const grid = document.querySelector('#asset-card-grid .row');
    if (!grid) return;

    // Clear existing content
    grid.innerHTML = '';

    if (assets.length === 0) {
        grid.innerHTML = '<div class="col-12 text-center text-muted p-3">표시할 자산이 없습니다.</div>';
        return;
    }

    assets.forEach(asset => {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4 mb-4';

        const card = document.createElement('div');
        card.className = 'card asset-card h-100';
        card.dataset.assetId = asset.id;

        card.innerHTML = `
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <h5 class="card-title mb-0">${asset.name}</h5>
                    <span class="status-dot ${asset.status}" title="${asset.status}"></span>
                </div>
                <hr>
                <p class="card-text mb-1"><strong>온도:</strong> ${asset.temp}°C</p>
                <p class="card-text"><strong>전력:</strong> ${asset.power} kW</p>
            </div>
        `;

        col.appendChild(card);
        grid.appendChild(col);
    });
}
