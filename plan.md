리포트' 페이지는 SignalCraft의 두뇌와도 같습니다. 단순히 과거 데이터를 보여주는 것을 넘어, 데이터 속에서 의미 있는 패턴을 발견하고, 미래를 예측하며, 비즈니스 의사결정을 돕는 강력한 분석 도구가 되어야 합니다.

사용자가 압도당하지 않도록, 페이지를 두 가지 핵심 영역으로 나누어 설계하는 것을 제안합니다.

보고서 생성기 (Report Generator): 사용자가 원하는 데이터를 직접 조합하여 맞춤형 보고서를 만드는 '인터랙티브 분석 공간'

정기 리포트 대시보드 (Scheduled Dashboards): 매주/매월 자동으로 생성되는 핵심 성과 보고서를 모아보는 '경영 브리핑 룸'

### 1. 보고서 생성기: "데이터 과학자처럼 질문하고 답을 얻으세요"
이 영역은 사용자가 직접 '기간', '자산', '데이터 종류' 등을 선택하여 원하는 인사이트를 즉시 얻을 수 있는 동적인 공간입니다.

컨트롤 패널 (Control Panel): 보고서의 재료 선택하기
페이지 상단에 보고서 생성을 위한 명확한 컨트롤 패널을 배치합니다.

① 기간 선택 (Date Range): 지난 7일, 이번 달, 지난 분기 와 같은 빠른 선택 옵션과, 달력에서 직접 시작일과 종료일을 선택할 수 있는 '사용자 지정' 기능을 제공합니다.

② 자산 선택 (Asset Selection):

개별 자산(예: 압축기 #3)을 선택하거나,

자산 그룹(예: A라인 전체), 위치별(예: 서울 데이터센터)로 다중 선택할 수 있는 기능을 제공합니다.

③ 지표 선택 (Metrics): 사용자가 보고서에 포함하고 싶은 데이터 종류를 체크박스로 선택하게 합니다.

[ ] 평균 소음(dB)

[ ] 최고 온도(°C)

[ ] 총 가동 시간(Hours)

[ ] 이상 징후 발생 횟수

④ 데이터 집계 단위 (Granularity): 데이터를 시간별, 일별, 주별 중 어떤 단위로 묶어서 볼지 선택하게 합니다.

⑤ 생성 및 내보내기 버튼: 모든 옵션을 선택한 후 [보고서 생성] 버튼을 누르면 아래에 결과가 표시되고, [PDF로 내보내기], [CSV로 내보내기] 버튼이 활성화됩니다.

보고서 결과물 (Report Output): 시각화된 인사이트
생성된 보고서는 텍스트와 차트가 결합된 형태로 표시됩니다.

요약: "2025년 9월 1일부터 9월 30일까지, A라인 자산 5개의 평균 가동 시간은 98.5%였으며, 총 12건의 이상 징후가 발생했습니다." 와 같은 핵심 요약 텍스트를 제공합니다.

메인 차트: 사용자가 선택한 지표들을 시간 축에 따라 보여주는 상호작용이 가능한 라인 차트를 제공합니다. 특정 지점에 마우스를 올리면 상세 수치를 볼 수 있습니다.

상세 데이터 테이블: 차트 아래에는 집계된 상세 데이터를 테이블 형태로 표시하여, 사용자가 정확한 수치를 확인하거나 복사할 수 있도록 합니다.

### 2. 정기 리포트 대시보드: "매주 월요일 아침, 비즈니스 현황을 한눈에"
이 영역은 매번 옵션을 선택할 필요 없이, 가장 중요한 비즈니스 지표들을 정기적으로 요약해주는 고정된 공간입니다. 각 보고서는 별도의 '카드' 형태로 제공됩니다.

자산 건전성 리포트 (Asset Health Report):

모든 자산의 과거 데이터(이상 징후 빈도, 심각도, 가동 시간 등)를 종합하여 **'건강 점수(Health Score)'**를 0점에서 100점 사이로 매깁니다.

"지난주 대비 건강 점수가 가장 많이 하락한 자산 Top 3"를 보여주어, 잠재적인 문제가 어디서 발생하고 있는지 알려줍니다.

이상 징후 핫스팟 분석 (Anomaly Hotspot Analysis):

가장 자주 문제를 일으키는 자산은 무엇인지, 가장 빈번하게 발생하는 이상 징후 유형('베어링 마모 의심' 등)은 무엇인지 파레토 차트(Pareto Chart)나 히트맵(Heatmap)으로 보여줍니다.

인사이트: "전체 문제의 80%가 특정 2개의 압축기에서 발생하고 있습니다" 와 같은 핵심 원인을 파악하게 해줍니다.

유지보수 비용 및 효과 리포트 (Maintenance ROI Report):

이상 징후 발생 후 조치(유지보수)까지 걸린 시간(MTTR - Mean Time To Repair)을 추적합니다.

유지보수를 진행한 자산과 그렇지 않은 자산의 이상 징후 발생 빈도를 비교하여, 예지보전 활동이 실제로 얼마나 효과가 있었는지를 데이터로 증명합니다.

### 🚀 구현 예시 (HTML with Inline CSS & JS)
아래 코드는 위에서 제안한 두 가지 핵심 영역을 모두 포함하는 '리포트' 페이지의 완성된 예시입니다. 별도의 CSS나 JS 파일 없이, 이 HTML 파일 하나만으로 바로 브라우저에서 열어볼 수 있습니다.

코드 예시

<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SignalCraft - 리포트</title>
    <!-- Font Awesome 아이콘 라이브러리 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Chart.js 라이브러리 (차트 시각화) -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <div class="report-page-container">
        <h1><i class="fas fa-chart-line"></i> 리포트 센터</h1>

        <!-- 1. 보고서 생성기 -->
        <section class="report-generator">
            <h2><i class="fas fa-tools"></i> 맞춤형 보고서 생성기</h2>
            <div class="control-panel">
                <div class="control-group">
                    <label for="date-range">기간 선택</label>
                    <select id="date-range">
                        <option>지난 7일</option>
                        <option selected>지난 30일</option>
                        <option>이번 분기</option>
                    </select>
                </div>
                <div class="control-group">
                    <label for="asset-group">자산 그룹</label>
                    <select id="asset-group">
                        <option>모든 자산</option>
                        <option>A라인</option>
                        <option>서울 데이터센터</option>
                    </select>
                </div>
                <div class="control-group">
                    <label for="granularity">집계 단위</label>
                    <select id="granularity">
                        <option>일별</option>
                        <option>주별</option>
                        <option>월별</option>
                    </select>
                </div>
            </div>
            <div class="control-group" style="margin-top: 1.5rem;">
                <label>지표 선택</label>
                <div class="checkbox-group">
                    <div class="checkbox-item"><input type="checkbox" id="metric1" checked> <label for="metric1" style="margin: 0 0 0 8px;">평균 소음(dB)</label></div>
                    <div class="checkbox-item"><input type="checkbox" id="metric2" checked> <label for="metric2" style="margin: 0 0 0 8px;">최고 온도(°C)</label></div>
                    <div class="checkbox-item"><input type="checkbox" id="metric3"> <label for="metric3" style="margin: 0 0 0 8px;">가동 시간</label></div>
                    <div class="checkbox-item"><input type="checkbox" id="metric4" checked> <label for="metric4" style="margin: 0 0 0 8px;">이상 징후 횟수</label></div>
                </div>
            </div>
            <div class="action-buttons">
                <button class="generate-btn"><i class="fas fa-play"></i> 보고서 생성</button>
                <button class="export-btn"><i class="fas fa-file-pdf"></i> PDF로 내보내기</button>
                <button class="export-btn"><i class="fas fa-file-csv"></i> CSV로 내보내기</button>
            </div>
        </section>

        <!-- 2. 정기 리포트 대시보드 -->
        <h2><i class="fas fa-tachometer-alt"></i> 정기 리포트 대시보드 (월간)</h2>
        <section class="dashboard-grid">
            <div class="report-card">
                <h3><i class="fas fa-heartbeat"></i> 자산 건전성 리포트</h3>
                <p style="text-align: center; color: #a0a0d0;">전체 자산 평균</p>
                <div class="health-score score-good">88점</div>
                <p style="color: #a0a0d0; font-weight: bold;">건강 점수 하락 Top 3</p>
                <ul class="top-list">
                    <li><span>압축기 #5</span> <strong>-15점</strong></li>
                    <li><span>냉동고-B2</span> <strong>-8점</strong></li>
                    <li><span>압축기 #2</span> <strong>-5점</strong></li>
                </ul>
            </div>
            <div class="report-card">
                <h3><i class="fas fa-fire"></i> 이상 징후 핫스팟</h3>
                <p style="color: #a0a0d0; font-weight: bold;">최다 발생 자산 Top 3</p>
                 <ul class="top-list">
                    <li><span>압축기 #3</span> <strong>12 건</strong></li>
                    <li><span>냉동고-A1</span> <strong>8 건</strong></li>
                    <li><span>압축기 #5</span> <strong>7 건</strong></li>
                </ul>
                <canvas id="anomalyTypeChart"></canvas>
            </div>
             <div class="report-card">
                <h3><i class="fas fa-tools"></i> 유지보수 효과 분석</h3>
                <p style="color: #a0a0d0; font-weight: bold;">평균 조치 소요 시간 (MTTR)</p>
                <div class="health-score score-avg">6.5 시간</div>
                <p style="color: #a0a0d0; font-weight: bold;">유지보수 후 징후 감소율</p>
                <div class="health-score score-good">+ 75%</div>
            </div>
        </section>

    </div>

    <script>
        // 샘플 데이터로 도넛 차트 그리기
        const ctx = document.getElementById('anomalyTypeChart').getContext('2d');
        const anomalyTypeChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['베어링 마모 의심', '과도한 진동', '온도 급상승', '기타'],
                datasets: [{
                    label: '징후 유형',
                    data: [12, 9, 6, 3],
                    backgroundColor: [
                        '#e74c3c',
                        '#f39c12',
                        '#8259de',
                        '#3498db'
                    ],
                    borderColor: '#2c2c54',
                    borderWidth: 4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#e0e0e0'
                        }
                    },
                    title: {
                        display: true,
                        text: '징후 유형별 분포',
                        color: '#ffffff'
                    }
                }
            }
        });
    </script>
</body>
</html>
