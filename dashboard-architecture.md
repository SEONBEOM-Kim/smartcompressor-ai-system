# SignalCraft 대시보드 아키텍처

## 1. 개요

SignalCraft 대시보드는 동적 HTML 컴포넌트 로딩 방식을 사용하는 현대적인 프론트엔드 아키텍처를 채택하고 있습니다. 메인 대시보드 페이지(`dashboard.html`)가 기본 뼈대를 제공하면, 사용자의 상호작용에 따라 필요한 UI 조각(HTML 파일)을 비동기적으로 불러와 특정 영역에 주입하는 방식입니다.

이러한 구조는 페이지 전체를 새로고침하지 않고 필요한 부분만 업데이트하므로 사용자 경험(UX)이 뛰어나고, 각 기능이 독립적인 컴포넌트로 분리되어 있어 유지보수와 확장이 용이합니다.

## 2. 디렉토리 구조

`dashboard-components` 디렉토리는 대시보드를 구성하는 모든 UI 컴포넌트 조각들을 포함하고 있습니다. 구조는 다음과 같습니다.

```
C:\Users\gmdqn\signalcraft\static\dashboard-components
│
├───sidebar.html
│
├───anomalies/
│   ├───anomaly-feed.html
│   ├───anomaly-trend.html
│   ├───threat-details-card.html
│   ├───threat-summary-card.html
│   └───today-briefing.html
│
├───assets/
│   ├───asset-details-card.html
│   ├───asset-feed.html
│   ├───asset-summary.html
│   ├───asset-summary-card.html
│   └───asset-trend.html
│
├───reports/
│   └───reports-main.html
│
└───settings/
    └───settings-main.html
```

## 3. 핵심 컴포넌트 및 흐름

### 핵심 파일
- **`dashboard.html` (가상)**: 대시보드의 기본 뼈대가 되는 메인 페이지입니다. `sidebar.html`과 같은 공통 컴포넌트를 포함하고, 다른 컴포넌트들이 로드될 메인 컨텐츠 영역(`#main-content`)을 가지고 있을 것으로 예상됩니다.
- **`sidebar.html`**: 대시보드의 핵심 내비게이션 메뉴입니다. 사용자는 여기에서 '자산 목록', '리포트' 등 다른 섹션으로 이동합니다.
- **`dashboard.js` (가상)**: `sidebar.html`의 링크 클릭과 같은 사용자 이벤트를 감지하고, 적절한 HTML 컴포넌트 파일을 서버에서 가져와(`fetch`) 메인 컨텐츠 영역에 동적으로 렌더링하는 로직을 담당합니다.
- **컴포넌트 HTML 파일**: `dashboard-components` 내의 모든 `.html` 파일들은 독립적인 UI 조각으로, `dashboard.js`에 의해 동적으로 로드됩니다.

### 데이터 흐름 (Mermaid)

```mermaid
graph TD
    A[사용자, 브라우저에서 dashboard.html 접속] --> B(dashboard.html 로드);
    B --> C{공통 레이아웃 로드};
    C --> D[sidebar.html];
    C --> E[header.html 등 기타 공통 UI];
    D -- "메뉴 클릭 (e.g., '자산 목록')" --> F[dashboard.js 이벤트 리스너];
    F -- "fetch('/dashboard-components/assets/asset-feed.html')" --> G[서버/파일 시스템];
    G -- "HTML 조각 반환" --> F;
    F -- ".innerHTML = response" --> H(메인 컨텐츠 영역(#main-content) 업데이트);
```

## 4. 컴포넌트 상세 설명

### 1. 공통 컴포넌트
- **`sidebar.html`**: 모든 대시보드 페이지에 공통으로 사용되는 사이드바 메뉴입니다. 다른 모든 컴포넌트의 진입점 역할을 합니다.

### 2. `anomalies/` (이상 징후)
이상 징후 감지와 관련된 모든 UI 컴포넌트를 포함합니다.
- `today-briefing.html`: 오늘의 이상 징후 요약 정보를 보여주는 카드 형태의 컴포넌트일 가능성이 높습니다.
- `anomaly-feed.html`: 감지된 모든 이상 징후를 목록(피드) 형태로 보여주는 메인 컴포넌트입니다.
- `anomaly-trend.html`: 시간 경과에 따른 이상 징후 발생 추이를 보여주는 차트 컴포넌트입니다.
- `threat-details-card.html`: 특정 위협(threat)에 대한 상세 정보를 보여주는 카드입니다.
- `threat-summary-card.html`: 위협 요약 정보를 보여주는 카드입니다.

### 3. `assets/` (자산)
자산 관리와 관련된 UI 컴포넌트를 포함합니다.
- `asset-feed.html`: 등록된 모든 자산의 목록을 보여주는 메인 컴포넌트입니다.
- `asset-details-card.html`: 특정 자산의 상세 정보를 보여주는 카드입니다.
- `asset-summary.html` / `asset-summary-card.html`: 전체 자산 현황을 요약하여 보여주는 컴포넌트입니다.
- `asset-trend.html`: 자산의 상태나 데이터 추이를 보여주는 차트 컴포넌트입니다.

### 4. `reports/` (리포트)
- `reports-main.html`: 리포트 생성 및 조회를 위한 메인 화면을 구성하는 컴포넌트입니다.

### 5. `settings/` (설정)
- `settings-main.html`: 알림, 사용자 정보 등 각종 설정을 관리하는 메인 화면을 구성하는 컴포넌트입니다.
