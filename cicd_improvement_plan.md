# GitHub Actions CI/CD 파이프라인 개선 계획

## 1. 개요
현재 SignalCraft 프로젝트에 구축된 GitHub Actions 기반 CI/CD 파이프라인은 안정적으로 작동하고 있습니다. 이 문서는 현재 파이프라인을 더욱 견고하고 효율적으로 만들기 위한 구체적인 개선 방안을 제안합니다.

---

## 2. 제안 개선 사항

### 가. 자동화된 테스트 단계 추가
- **현황:** 현재 파이프라인에는 코드의 무결성을 검증하는 자동화된 테스트 단계가 없습니다.
- **문제점:** 버그가 포함된 코드가 테스트 없이 프로덕션 환경에 배포될 위험이 있습니다.
- **개선 방안:** 배포 잡(job)이 실행되기 전에, 테스트 잡을 추가하여 `pytest` (백엔드)와 `npm test` (프론트엔드)를 실행합니다. 테스트를 통과해야만 배포가 진행되도록 설정합니다.
- **구현 예시 (`auto-deploy.yml`):**
    ```yaml
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - name: Run Backend & Frontend Tests
            run: |
              # Backend Test
              pip install -r requirements.txt
              pytest tests/
              # Frontend Test
              npm install
              npm test

      deploy:
        needs: test # `test` 잡이 성공해야만 `deploy` 잡 실행
        runs-on: ubuntu-latest
        steps:
          # ... 기존 배포 로직 ...
    ```

### 나. 빌드 및 최적화 단계 추가
- **현황:** 소스 코드를 그대로 서버에 배포하고 있습니다.
- **문제점:** 프로덕션 환경에서 불필요한 빌드 시간을 소요하거나, 최적화되지 않은 코드가 실행될 수 있습니다.
- **개선 방안:** 배포 스크립트에 프론트엔드 정적 파일을 빌드하는 `npm run build`와 Python 코드를 바이트코드로 미리 컴파일하는 `python -m compileall` 단계를 추가합니다.
- **구현 예시 (배포 스크립트 내):**
    ```bash
    echo "📦 의존성 설치 및 빌드..."
    npm install
    npm run build # 프론트엔드 빌드

    echo "🐍 Python 코드 최적화..."
    python -m compileall . # 바이트코드 컴파일
    ```

### 다. 배포 실패 시 자동 롤백 기능
- **현황:** 배포에 실패할 경우, 수동으로 복구해야 합니다.
- **문제점:** 서비스 다운타임이 길어질 수 있으며, 긴급 상황에서 운영자의 실수가 발생할 수 있습니다.
- **개선 방안:** 배포 시작 전의 마지막 커밋 해시를 변수로 저장해 둡니다. 배포 과정에서 에러가 발생하면, 저장해 둔 커밋으로 `git reset --hard`를 실행하여 코드를 이전 상태로 되돌리고 서비스를 재시작합니다.
- **구현 예시 (배포 스크립트 내):**
    ```bash
    # 배포 전 현재 커밋 저장
    PREVIOUS_COMMIT=$(git rev-parse HEAD)

    # ... 배포 로직 실행 ...
    # (예: npm install, pm2 restart 등)

    # 배포 로직 실패 시 롤백 실행
    if [ $? -ne 0 ]; then
        echo "❌ 배포 실패! 이전 버전으로 롤백합니다..."
        git reset --hard $PREVIOUS_COMMIT
        npm install # 롤백된 버전에 맞는 의존성 재설치
        pm2 restart all
        exit 1
    fi
    ```

### 라. 배포 상태 알림 추가
- **현황:** 배포의 성공 또는 실패 여부를 GitHub Actions 페이지에서 직접 확인해야 합니다.
- **문제점:** 배포 상태를 즉시 인지하기 어려워, 문제 발생 시 대응이 늦어질 수 있습니다.
- **개선 방안:** 워크플로우의 마지막에 `always()` 조건을 사용하여, 배포 잡의 성공/실패 여부를 Slack, Discord 등 외부 채널로 알리는 단계를 추가합니다.
- **구현 예시 (`auto-deploy.yml`):**
    ```yaml
      - name: Notify Deployment Status to Slack
        if: always() # 잡의 성공/실패 여부와 관계없이 항상 실행
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          fields: repo,message,commit,author,action,eventName,ref,workflow,job,took
          webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }} # GitHub Secrets에 웹훅 URL 저장
    ```

### 마. 환경별 배포 전략 도입 (Staging)
- **현황:** `main` 브랜치에 푸시하면 즉시 프로덕션 환경에 배포됩니다.
- **문제점:** 새로운 기능이나 변경 사항을 실제 운영 환경과 유사한 곳에서 충분히 테스트할 기회가 없습니다.
- **개선 방안:** `develop` 브랜치를 추가하고, 이 브랜치에 푸시하면 스테이징(Staging) 환경에 배포되도록 워크플로우를 확장합니다. 스테이징에서 검증이 완료된 후, `develop` 브랜치를 `main` 브랜치로 병합하여 프로덕션에 배포합니다.
- **구현 예시 (`auto-deploy.yml`):**
    ```yaml
    on:
      push:
        branches:
          - main    # Production 환경
          - develop # Staging 환경

    jobs:
      deploy:
        runs-on: ubuntu-latest
        steps:
          - name: Deploy to Staging
            if: github.ref == 'refs/heads/develop'
            # ... 스테이징 서버 배포 로직 ...

          - name: Deploy to Production
            if: github.ref == 'refs/heads/main'
            # ... 프로덕션 서버 배포 로직 ...
    ```

## 3. 기대 효과
- **안정성 향상:** 자동화된 테스트와 롤백 기능으로 프로덕션 환경의 안정성이 크게 향상됩니다.
- **개발 효율성 증대:** 스테이징 환경 도입으로 개발자들이 부담 없이 새로운 기능을 테스트하고 검증할 수 있습니다.
- **운영 효율성 개선:** 배포 상태 알림을 통해 팀이 배포 상황을 실시간으로 공유하고 신속하게 대응할 수 있습니다.
