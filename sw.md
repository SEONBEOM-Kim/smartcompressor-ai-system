static/js/notification_dashboard.js 모듈화 플랜
static/js/notification_dashboard.js는 약 552줄의 코드로 구성된 Slack/Discord 스타일의 알림 관리 대시보드입니다.[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:1-216]

현재 구조 분석
주요 기능 영역
탭 관리 (약 80줄): 5개 탭(개요, 채널, 템플릿, 히스토리, 설정) 전환[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:46-81]
데이터 로딩 (약 200줄): API 호출 및 데이터 페칭[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:83-113]
UI 렌더링 (약 150줄): 통계 카드, 채널 상태, 테이블 업데이트[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:115-161]
알림 전송 (약 40줄): 빠른 알림 전송 폼 처리[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:299-345]
유틸리티 함수 (약 120줄): 아이콘, 색상, 날짜 포맷 등[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:433-552]
모듈화 폴더 구조
static/js/notification_dashboard/  
  ├── data/  
  │   ├── api-client.js  
  │   └── data-loader.js  
  ├── ui/  
  │   ├── tab-manager.js  
  │   ├── overview-renderer.js  
  │   ├── channel-renderer.js  
  │   ├── template-renderer.js  
  │   └── history-renderer.js  
  ├── forms/  
  │   ├── notification-sender.js  
  │   ├── settings-manager.js  
  │   └── template-creator.js  
  ├── utils/  
  │   ├── formatters.js  
  │   └── toast-manager.js  
  └── notification_dashboard.js (진입점)  
Phase 1: 데이터 레이어 분리 (2-3일)
1.1 API 클라이언트 생성
/api/notifications/status, /api/notifications/channels, /api/notifications/history 등 모든 API 호출을 api-client.js로 통합
각 엔드포인트별 메서드 분리 (fetchStatus(), fetchChannels(), fetchHistory(), sendNotification() 등)
1.2 데이터 로더 생성
API 클라이언트를 사용하여 탭별 데이터 로딩 로직을 data-loader.js로 이동
loadOverview(), loadChannels(), loadTemplates(), loadHistory() 메서드 구현
에러 핸들링 및 로딩 상태 관리
Phase 2: UI 렌더링 레이어 분리 (2-3일)
2.1 탭 매니저 생성
탭 전환 로직을 tab-manager.js로 분리[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:47-82]
탭 이벤트 리스너 설정
현재 활성 탭 상태 관리
2.2 개요 렌더러 생성
통계 카드 업데이트 로직을 overview-renderer.js로 이동
채널 상태 표시 로직 분리
최근 알림 테이블 렌더링 로직 분리
2.3 채널 렌더러 생성
채널 목록 표시 로직을 channel-renderer.js로 이동[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:178-215]
채널 카드 생성 로직 분리
2.4 템플릿 렌더러 생성
템플릿 목록 표시 로직을 template-renderer.js로 이동
템플릿 카드 생성 및 관리 로직 분리
2.5 히스토리 렌더러 생성
알림 히스토리 테이블 렌더링 로직을 history-renderer.js로 이동
필터링 UI 업데이트 로직 분리
Phase 3: 폼 처리 레이어 분리 (1-2일)
3.1 알림 전송 핸들러 생성
빠른 알림 전송 폼 처리를 notification-sender.js로 이동[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:307-344]
폼 검증 로직 분리
전송 성공/실패 처리 로직 분리
3.2 설정 매니저 생성
설정 로드 및 저장 로직을 settings-manager.js로 이동[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:299-305]
설정 폼 이벤트 리스너 설정
3.3 템플릿 생성기 생성
템플릿 생성 폼 처리를 template-creator.js로 이동
템플릿 모달 관리 로직 분리
Phase 4: 유틸리티 레이어 분리 (1일)
4.1 포맷터 생성
채널 아이콘 매핑 함수를 formatters.js로 이동[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:434-444]
채널 표시 이름 변환 함수 이동
타입 색상 및 표시 이름 변환 함수 이동
우선순위 색상 변환 함수 이동
날짜 포맷팅 함수 이동[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:490-499]
4.2 토스트 매니저 생성
Bootstrap 토스트 생성 로직을 toast-manager.js로 이동[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:501-526]
토스트 컨테이너 생성 로직 분리
Phase 5: 진입점 간소화 (1일)
5.1 새로운 notification_dashboard.js 구조
모든 모듈 인스턴스 생성 및 초기화
전역 함수 등록 (기존 호환성 유지)
DOMContentLoaded 이벤트 핸들러 설정
자동 새로고침 설정
5.2 전역 함수 유지
loadHistory(), createTemplate() 등 HTML에서 호출되는 전역 함수 유지[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:539-545]
Phase 6: HTML 업데이트 (1일)
6.1 스크립트 로드 순서 변경
templates/notification_dashboard.html에서 모듈 파일들을 순서대로 로드[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: templates/notification_dashboard.html:473-476]:

유틸리티 → 데이터 → UI → 폼 → 진입점 순서
실행 체크리스트
 API 클라이언트 및 데이터 로더 생성
 탭 매니저 및 렌더러 5개 생성
 폼 핸들러 3개 생성
 유틸리티 함수 분리
 진입점 간소화 (552줄 → 100줄 목표)
 HTML 스크립트 로드 순서 업데이트
 전체 기능 테스트 (5개 탭 모두)
 배포 파이프라인 테스트
주의사항
전역 함수 호환성: HTML에서 onclick 등으로 호출되는 함수들은 전역으로 유지
Bootstrap 의존성: 토스트, 모달 등 Bootstrap 컴포넌트 사용 유지
빌드 프로세스 불필요: 전통적인 스크립트 태그 방식으로 즉시 적용 가능
