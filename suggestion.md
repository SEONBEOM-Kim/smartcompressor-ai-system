정적 html 은 static/ 에 flask 템플릿은 templates/ 에 옮기고싶어 . 플랜을 세워줘
Fast
Searched across SEONBEOM-Kim/smartcompressor-ai-system
Answer
정적 HTML 파일들을 static/에, Flask 템플릿을 templates/로 재구성하는 플랜을 제시하겠습니다.

현재 상황 분석
프로젝트에는 두 가지 유형의 HTML 파일이 혼재되어 있습니다:

정적 HTML (Flask 템플릿 기능 불필요):

static/human_labeling_interface.html human_labeling_interface.html:1-6
static/labeling_management_dashboard.html labeling_management_dashboard.html:1-6
static/noise_cancellation_test.html noise_cancellation_test.html:1-6
static/smart_storage_dashboard.html smart_storage_dashboard.html:1-6
static/index.html (메인 랜딩 페이지)
static/showcase.html (로그인 페이지) showcase.html:315-330
Flask 템플릿 (이미 올바른 위치):

templates/dashboard.html dashboard.html:1-16
templates/mobile_app.html mobile_app.html:1-23
templates/notification_dashboard.html notification_dashboard.html:1-11
Phase 1: 폴더 구조 생성 (1일)
1.1 새 폴더 생성
mkdir -p static/pages
1.2 최종 구조
static/  
  ├── pages/           # 정적 HTML (새로 생성)  
  │   ├── index.html  
  │   ├── showcase.html  
  │   ├── labeling/  
  │   │   ├── interface.html  
  │   │   └── management.html  
  │   ├── testing/  
  │   │   └── noise_cancellation.html  
  │   └── storage/  
  │       └── dashboard.html  
  ├── js/              # JavaScript 파일  
  ├── css/             # CSS 파일  
  └── icons/           # 아이콘 파일  
  
templates/           # Flask 템플릿 (기존 유지)  
  ├── dashboard.html  
  ├── mobile_app.html  
  └── notification_dashboard.html  
Phase 2: 파일 이동 (2-3일)
2.1 정적 HTML 파일 이동
이동 매핑:

# 메인 페이지  
static/index.html → static/pages/index.html  
static/showcase.html → static/pages/showcase.html  
  
# 라벨링 관련  
static/human_labeling_interface.html → static/pages/labeling/interface.html  
static/labeling_management_dashboard.html → static/pages/labeling/management.html  
  
# 테스트 페이지  
static/noise_cancellation_test.html → static/pages/testing/noise_cancellation.html  
  
# 스토리지  
static/smart_storage_dashboard.html → static/pages/storage/dashboard.html
2.2 Flask 템플릿 확인
templates/ 폴더의 파일들은 이미 올바른 위치에 있으므로 이동 불필요

Phase 3: 서버 라우팅 업데이트 (2-3일)
3.1 Node.js Express 서버 수정
server.js 업데이트: app.js:22-29

// 정적 파일 서빙 경로 업데이트  
app.use('/static', express.static(path.join(__dirname, '../static')));  
  
// 메인 페이지 라우팅 수정  
app.get('/', (req, res) => {  
    res.sendFile(path.join(__dirname, '../static/pages/showcase.html'));  
});  
  
// 추가 정적 페이지 라우팅  
app.get('/index', (req, res) => {  
    res.sendFile(path.join(__dirname, '../static/pages/index.html'));  
});
3.2 Flask 앱 라우팅 확인
Flask 템플릿 라우팅은 이미 올바르게 설정되어 있습니다: app.py:132-148

Phase 4: 내부 링크 업데이트 (2-3일)
4.1 관리자 대시보드 링크 수정
admin/templates/admin_dashboard.html 업데이트: admin_dashboard.html:385-412

<!-- 기존 -->  
<a href="/static/human_labeling_interface.html">  
  
<!-- 수정 후 -->  
<a href="/static/pages/labeling/interface.html">
4.2 쇼케이스 페이지 링크 수정
static/showcase.html 업데이트: showcase.html:384-397

<!-- 기존 -->  
<a href="/static/audio_recorder_client.html">  
<a href="/static/human_labeling_interface.html">  
  
<!-- 수정 후 -->  
<a href="/static/pages/audio_recorder_client.html">  
<a href="/static/pages/labeling/interface.html">
4.3 모든 HTML 파일 내부 링크 검색 및 수정
# 링크 검색  
grep -r "href=\"/static/.*\.html\"" static/ templates/ admin/  
  
# 각 파일에서 경로 업데이트
Phase 5: CSS/JS 상대 경로 수정 (1-2일)
5.1 이동된 HTML 파일의 리소스 경로 확인
파일 이동 후 CSS/JS 참조가 깨지지 않도록 확인:

<!-- 기존 (static/ 루트에 있을 때) -->  
<link href="/static/css/dashboard.css" rel="stylesheet">  
<script src="/static/js/dashboard.js"></script>  
  
<!-- 이동 후 (static/pages/에 있을 때) - 변경 불필요 -->  
<link href="/static/css/dashboard.css" rel="stylesheet">  
<script src="/static/js/dashboard.js"></script>
절대 경로(/static/)를 사용하므로 대부분 수정 불필요

Phase 6: Nginx 설정 업데이트 (1일)
6.1 Nginx 정적 파일 서빙 확인
Nginx 설정에서 정적 파일 경로가 올바른지 확인:

location /static/ {  
    alias /var/www/smartcompressor/static/;  
    expires 30d;  
}
Phase 7: 배포 파이프라인 테스트 (1-2일)
7.1 GitHub Actions 워크플로우 확인
배포 스크립트가 새 폴더 구조를 인식하는지 확인:

7.2 로컬 테스트
# 서버 재시작  
pm2 restart all  
  
# 각 페이지 접근 테스트  
curl http://localhost:3000/  
curl http://localhost:3000/static/pages/labeling/interface.html  
curl http://localhost:3000/dashboard
실행 체크리스트
Phase 1 완료 기준
 static/pages/ 폴더 생성
 하위 폴더 구조 생성 (labeling/, testing/, storage/)
Phase 2 완료 기준
 모든 정적 HTML 파일 이동
 원본 파일 백업 (삭제 전)
 Flask 템플릿 위치 확인
Phase 3 완료 기준
 server.js 라우팅 업데이트
 Flask 라우팅 확인
 서버 재시작 및 테스트
Phase 4 완료 기준
 관리자 대시보드 링크 수정
 쇼케이스 페이지 링크 수정
 모든 내부 링크 검증
Phase 5 완료 기준
 CSS/JS 경로 확인
 브라우저에서 리소스 로딩 테스트
Phase 6 완료 기준
 Nginx 설정 확인
 Nginx 재시작
Phase 7 완료 기준
 로컬 환경 전체 테스트
 프로덕션 배포 테스트
 모든 페이지 접근 가능 확인
주의사항
점진적 마이그레이션: 한 번에 모든 파일을 이동하지 말고 단계별로 진행
백업 필수: 파일 이동 전 전체 프로젝트 백업
링크 검증: 모든 내부 링크가 정상 작동하는지 확인
배포 파이프라인 영향: GitHub Actions 워크플로우가 새 구조를 인식하는지 확인
Notes
현재 프로젝트는 정적 HTML과 Flask 템플릿이 혼재되어 있어 구조가 명확하지 않습니다. 이 플랜을 따라 재구성하면 파일 유형별로 명확히 분리되어 유지보수가 훨씬 쉬워집니다. 특히 static/pages/ 폴더를 기능별로 하위 분류하면 프로젝트가 성장해도 관리가 용이합니다. Flask 템플릿은 이미 templates/ 폴더에 올바르게 위치하고 있으므로 추가 작업이 필요 없습니다