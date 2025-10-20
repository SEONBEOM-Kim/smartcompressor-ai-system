// static/js/dashboard/ui/section-manager.js
class SectionManager {
    constructor() {
        this.currentSection = 'overview';
        this.tableRenderer = null;
        this.cardUpdater = null;
        this.dataLoader = null;
    }

    setDependencies(tableRenderer, cardUpdater, dataLoader, chartManager) {
        this.tableRenderer = tableRenderer;
        this.cardUpdater = cardUpdater;
        this.dataLoader = dataLoader;
        this.chartManager = chartManager;
    }

    showSection(sectionName) {
        // 모든 섹션 숨기기
        document.querySelectorAll('.dashboard-section').forEach(section => {
            section.style.display = 'none';
        });

        // 선택된 섹션 표시
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.style.display = 'block';
            this.currentSection = sectionName;

            // 섹션별 데이터 로드
            switch(sectionName) {
                case 'overview':
                    this.loadOverviewData();
                    break;
                case 'stores':
                    this.loadStoresData();
                    break;
                case 'devices':
                    this.loadDevicesData();
                    break;
                case 'analytics':
                    this.loadAnalyticsData();
                    break;
                case 'notifications':
                    this.loadNotificationsData();
                    break;
                case 'assets':
                    this.loadAssetsData();
                    break;
            }
        }

        // 네비게이션 활성화 상태 업데이트
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        const activeLink = document.querySelector(`[href="#${sectionName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    async loadOverviewData() {
        try {
            if (this.dataLoader) {
                const data = await this.dataLoader.loadOverviewData();
                if (data.success) {
                    this.cardUpdater.updateOverviewCards(data.summary);
                }
            }
        } catch (error) {
            console.error('개요 데이터 로드 실패:', error);
        }
    }

    async loadStoresData() {
        try {
            if (this.dataLoader) {
                const data = await this.dataLoader.loadStoresData();
                if (data.success) {
                    this.tableRenderer.updateStoresTable(data.stores);
                }
            }
        } catch (error) {
            console.error('매장 데이터 로드 실패:', error);
        }
    }

    async loadDevicesData() {
        try {
            if (this.dataLoader) {
                const data = await this.dataLoader.loadDevicesData();
                if (data.success) {
                    this.tableRenderer.updateDevicesTable(data.devices);
                }
            }
        } catch (error) {
            console.error('디바이스 데이터 로드 실패:', error);
        }
    }

    async loadAnalyticsData() {
        try {
            if (this.dataLoader) {
                const data = await this.dataLoader.loadAnalyticsData();
                if (data.success) {
                    this.updateAnalyticsCharts(data.analytics);
                }
            }
        } catch (error) {
            console.error('분석 데이터 로드 실패:', error);
        }
    }

    async loadNotificationsData() {
        try {
            if (this.dataLoader) {
                const data = await this.dataLoader.loadNotificationsData();
                if (data.success) {
                    this.tableRenderer.updateNotificationsTable(data.notifications);
                }
            }
        } catch (error) {
            console.error('알림 데이터 로드 실패:', error);
        }
    }

    async loadAssetsData() {
        try {
            if (this.dataLoader) {
                const data = await this.dataLoader.loadAssetsData();
                if (data.success) {
                    this.tableRenderer.updateAssetsTable(data.assets);
                    this.cardUpdater.updateAssetSummaryCards(data.summary);
                }
            }
        } catch (error) {
            console.error('자산 데이터 로드 실패:', error);
        }
    }

    updateAnalyticsCharts(analytics) {
        if (analytics.temperature && this.chartManager && this.chartManager.charts.temperature) {
            this.chartManager.charts.temperature.update(analytics.temperature);
        }

        if (analytics.vibration && this.chartManager && this.chartManager.charts.vibration) {
            this.chartManager.charts.vibration.update(analytics.vibration);
        }

        if (analytics.power && this.chartManager && this.chartManager.charts.power) {
            this.chartManager.charts.power.update(analytics.power);
        }

        if (analytics.anomaly && this.chartManager && this.chartManager.charts.anomaly) {
            this.chartManager.charts.anomaly.update(analytics.anomaly);
        }
        
        if (analytics.asset && this.chartManager && this.chartManager.charts.asset) {
            this.chartManager.charts.asset.update(analytics.asset);
        }
    }

    setupNavigation() {
        // 네비게이션 이벤트 리스너 설정
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('href').substring(1);
                this.showSection(section);
            });
        });
    }
}