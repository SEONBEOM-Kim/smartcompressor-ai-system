const Sentry = require('@sentry/node');

class ErrorTrackingService {
    /**
     * 예외를 Sentry에 기록합니다.
     * @param {Error} error - 기록할 예외 객체
     * @param {Object} context - 추가 컨텍스트 정보
     * @param {Object} userInfo - 사용자 관련 정보
     */
    static captureException(error, context = null, userInfo = null) {
        Sentry.withScope(scope => {
            if (context) {
                scope.setContext('additional_info', context);
            }

            if (userInfo) {
                scope.setUser(userInfo);
            }

            Sentry.captureException(error);
        });
    }

    /**
     * 메시지를 Sentry에 기록합니다.
     * @param {string} message - 기록할 메시지
     * @param {string} level - 로그 레벨 ('debug', 'info', 'warning', 'error', 'fatal')
     * @param {Object} context - 추가 컨텍스트 정보
     */
    static captureMessage(message, level = 'info', context = null) {
        Sentry.withScope(scope => {
            if (context) {
                scope.setContext('additional_info', context);
            }

            Sentry.captureMessage(message, level);
        });
    }

    /**
     * Sentry 이벤트에 태그를 추가합니다.
     * @param {string} key - 태그 키
     * @param {string} value - 태그 값
     */
    static setTag(key, value) {
        Sentry.setTag(key, value);
    }

    /**
     * Sentry 이벤트에 추가 데이터를 설정합니다.
     * @param {string} key - 데이터 키
     * @param {any} value - 데이터 값
     */
    static setExtra(key, value) {
        Sentry.setExtra(key, value);
    }

    /**
     * Sentry 트랜잭션을 시작합니다. (성능 모니터링용)
     * @param {string} name - 트랜잭션 이름
     * @param {string} op - 작업 유형
     * @returns {Sentry.Transaction} Transaction 객체
     */
    static startTransaction(name, op = 'default') {
        return Sentry.startTransaction({ name, op });
    }
}

module.exports = ErrorTrackingService;