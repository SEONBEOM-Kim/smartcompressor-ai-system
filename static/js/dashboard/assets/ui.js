// static/js/dashboard/assets/ui.js

export function renderAssetSummary(summary) {
    document.getElementById('total-assets-summary').textContent = summary.totalAssets || 0;
    document.getElementById('normal-assets-summary').textContent = summary.normalAssets || 0;
    document.getElementById('anomaly-assets-summary').textContent = summary.anomalyAssets || 0;
    document.getElementById('offline-assets-summary').textContent = summary.offlineAssets || 0;
}

export function renderAssetFeed(assets) {
    const feedList = document.getElementById('asset-feed-list');
    if (!feedList) return;

    // Clear existing content
    feedList.innerHTML = '';

    if (assets.length === 0) {
        feedList.innerHTML = '<div class="p-3 text-center text-muted">등록된 자산이 없습니다.</div>';
        return;
    }

    assets.forEach(asset => {
        const item = document.createElement('div');
        item.className = 'asset-feed-item';

        let iconClass = 'fas fa-circle-check';
        let iconColorClass = 'normal';
        if (asset.status === 'warning') {
            iconClass = 'fas fa-triangle-exclamation';
            iconColorClass = 'warning';
        } else if (asset.status === 'anomaly') {
            iconClass = 'fas fa-circle-xmark';
            iconColorClass = 'anomaly';
        } else if (asset.status === 'offline') {
            iconClass = 'fas fa-circle';
            iconColorClass = 'offline';
        }

        item.innerHTML = `
            <div class="icon ${iconColorClass}">
                <i class="${iconClass}"></i>
            </div>
            <div class="flex-grow-1">
                <div><strong>${asset.assetName}</strong>: ${asset.type || 'N/A'}</div>
                <div class="timestamp">${asset.lastUpdate || 'N/A'}</div>
            </div>
        `;
        feedList.appendChild(item);
    });
}

export function renderAssetList(assets) {
    const tableBody = document.querySelector('#asset-table tbody');
    if (!tableBody) return;

    // Clear existing content
    tableBody.innerHTML = '';

    if (assets.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="8" class="text-center text-muted p-3">표시할 자산이 없습니다.</td></tr>';
        return;
    }

    assets.forEach(asset => {
        const row = document.createElement('tr');

        let statusBadge = '';
        if (asset.status === 'normal') {
            statusBadge = '<span class="status-badge active">🟢 정상</span>';
        } else if (asset.status === 'warning') {
            statusBadge = '<span class="status-badge warning">🟡 경고</span>';
        } else if (asset.status === 'anomaly') {
            statusBadge = '<span class="status-badge danger">🔴 위험</span>';
        } else if (asset.status === 'offline') {
            statusBadge = '<span class="status-badge offline">⚪ 오프라인</span>';
        }

        row.innerHTML = `
            <td>${asset.id || 'N/A'}</td>
            <td>${asset.name || 'N/A'}</td>
            <td>${asset.type || 'N/A'}</td>
            <td>${statusBadge}</td>
            <td>${asset.location || 'N/A'}</td>
            <td>${asset.model || 'N/A'}</td>
            <td>${asset.statusDesc || 'N/A'}</td>
            <td><button class="btn btn-sm btn-outline-primary asset-detail-btn" data-asset-id="${asset.id}">상세보기</button></td>
        `;
        tableBody.appendChild(row);
    });

    // Add event listeners to the detail buttons
    document.querySelectorAll('.asset-detail-btn').forEach(button => {
        button.addEventListener('click', function() {
            const assetId = this.getAttribute('data-asset-id');
            showAssetDetail(assetId);
        });
    });
}

function showAssetDetail(assetId) {
    // Show the detail view
    const detailView = document.getElementById('asset-detail-view');
    if (detailView) {
        detailView.style.display = 'block';
    }

    // TODO: Load asset details based on assetId
    console.log(`Showing details for asset ID: ${assetId}`);
}