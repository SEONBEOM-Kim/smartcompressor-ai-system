// Main entry point for the dashboard JavaScript

import { renderSummaryCards, renderAnomalyFeed, renderAssetList } from './ui.js';
import { AssetChart } from './charts/asset-chart.js';

// Dummy data to simulate API response
const dummyDashboardData = {
    summary: {
        totalAssets: 12,
        normalAssets: 10,
        anomalyAssets: 2,
        offlineAssets: 0,
    },
    anomalies: [
        { id: 1, assetName: '냉동고 #3', type: '온도 경고', timestamp: '2025-10-16 10:45:12', severity: 'warning' },
        { id: 2, assetName: '냉동고 #1', type: '압축기 과부하', timestamp: '2025-10-16 09:12:34', severity: 'anomaly' },
        { id: 3, assetName: '냉동고 #8', type: '전력 스파이크', timestamp: '2025-10-15 22:05:01', severity: 'warning' },
    ],
    assets: [
        { id: 1, name: '냉동고 #1', type: '냉동고', status: 'anomaly', statusDesc: '고온 경보', location: '서울 본사', model: 'FRZ-2025-A', lastUpdate: '2025-10-16 10:45:12' },
        { id: 2, name: '냉동고 #2', type: '냉동고', status: 'normal', statusDesc: '정상 작동', location: '서울 본사', model: 'FRZ-2025-B', lastUpdate: '2025-10-16 10:45:10' },
        { id: 3, name: '냉동고 #3', type: '냉동고', status: 'warning', statusDesc: '전력 과다 소비', location: '서울 본사', model: 'FRZ-2025-C', lastUpdate: '2025-10-16 10:45:08' },
        { id: 4, name: '냉동고 #4', type: '냉동고', status: 'normal', statusDesc: '정상 작동', location: '서울 본사', model: 'FRZ-2025-D', lastUpdate: '2025-10-16 10:45:06' },
        { id: 5, name: '냉동고 #5', type: '냉동고', status: 'normal', statusDesc: '정상 작동', location: '서울 본사', model: 'FRZ-2025-E', lastUpdate: '2025-10-16 10:45:04' },
        { id: 6, name: '냉동고 #6', type: '냉동고', status: 'normal', statusDesc: '정상 작동', location: '서울 본사', model: 'FRZ-2025-F', lastUpdate: '2025-10-16 10:45:02' },
        { id: 7, name: '냉동고 #7', type: '냉동고', status: 'normal', statusDesc: '정상 작동', location: '서울 본사', model: 'FRZ-2025-G', lastUpdate: '2025-10-16 10:45:00' },
        { id: 8, name: '냉동고 #8', type: '냉동고', status: 'warning', statusDesc: '도어 오픈 경보', location: '서울 본사', model: 'FRZ-2025-H', lastUpdate: '2025-10-16 10:44:58' },
        { id: 9, name: '냉동고 #9', type: '냉동고', status: 'normal', statusDesc: '정상 작동', location: '서울 본사', model: 'FRZ-2025-I', lastUpdate: '2025-10-16 10:44:56' },
        { id: 10, name: '냉동고 #10', type: '냉동고', status: 'normal', statusDesc: '정상 작동', location: '서울 본사', model: 'FRZ-2025-J', lastUpdate: '2025-10-16 10:44:54' },
        { id: 11, name: '냉동고 #11', type: '냉동고', status: 'normal', statusDesc: '정상 작동', location: '서울 본사', model: 'FRZ-2025-K', lastUpdate: '2025-10-16 10:44:52' },
        { id: 12, name: '냉동고 #12', type: '냉동고', status: 'normal', statusDesc: '정상 작동', location: '서울 본사', model: 'FRZ-2025-L', lastUpdate: '2025-10-16 10:44:50' },
    ]
};

function init() {
    // Render UI components with dummy data
    renderSummaryCards(dummyDashboardData.summary);
    renderAnomalyFeed(dummyDashboardData.anomalies);
    renderAssetList(dummyDashboardData.assets);
    
    // Create an instance of AssetChart if needed elsewhere
    // const assetChart = new AssetChart('assetChart');
}

// Initialize the dashboard when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', init);