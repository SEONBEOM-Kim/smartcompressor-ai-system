
// Main entry point for the dashboard JavaScript

import { renderSummaryCards, renderAnomalyFeed, renderAssetList } from './ui.js';

// Dummy data to simulate API response
const dummyDashboardData = {
    summary: {
        totalAssets: 12,
        normalAssets: 10,
        anomalyAssets: 2,
    },
    anomalies: [
        { id: 1, assetName: '냉동고 #3', type: '온도 경고', timestamp: '2025-10-16 10:45:12', severity: 'warning' },
        { id: 2, assetName: '냉동고 #1', type: '압축기 과부하', timestamp: '2025-10-16 09:12:34', severity: 'anomaly' },
        { id: 3, assetName: '냉동고 #8', type: '전력 스파이크', timestamp: '2025-10-15 22:05:01', severity: 'warning' },
    ],
    assets: [
        { id: 1, name: '냉동고 #1', status: 'anomaly', temp: -15, power: 1.2 },
        { id: 2, name: '냉동고 #2', status: 'normal', temp: -20, power: 0.8 },
        { id: 3, name: '냉동고 #3', status: 'warning', temp: -12, power: 1.1 },
        { id: 4, name: '냉동고 #4', status: 'normal', temp: -22, power: 0.7 },
        { id: 5, name: '냉동고 #5', status: 'normal', temp: -19, power: 0.85 },
        { id: 6, name: '냉동고 #6', status: 'normal', temp: -21, power: 0.75 },
        { id: 7, name: '냉동고 #7', status: 'normal', temp: -20, power: 0.8 },
        { id: 8, name: '냉동고 #8', status: 'warning', temp: -18, power: 1.3 },
        { id: 9, name: '냉동고 #9', status: 'normal', temp: -22, power: 0.8 },
        { id: 10, name: '냉동고 #10', status: 'normal', temp: -20, power: 0.9 },
        { id: 11, name: '냉동고 #11', status: 'normal', temp: -21, power: 0.8 },
        { id: 12, name: '냉동고 #12', status: 'normal', temp: -19, power: 0.85 },
    ]
};

function init() {
    // Render UI components with dummy data
    renderSummaryCards(dummyDashboardData.summary);
    renderAnomalyFeed(dummyDashboardData.anomalies);
    renderAssetList(dummyDashboardData.assets);
}

// Initialize the dashboard when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', init);
