// DOM이 로드된 후 실행
document.addEventListener('DOMContentLoaded', function() {
    // 네비게이션 스크롤 효과
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.boxShadow = 'none';
        }
    });

    // 모바일 네비게이션 토글
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }

    // 센서 도트 애니메이션
    animateSensorDots();

    // 스무스 스크롤
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // 대기자 등록 폼 처리
    const waitlistForm = document.getElementById('waitlistForm');
    if (waitlistForm) {
        waitlistForm.addEventListener('submit', handleWaitlistSubmission);
    }
});

// 센서 도트 애니메이션
function animateSensorDots() {
    const sensorDots = document.querySelectorAll('.sensor-dot');
    
    sensorDots.forEach((dot, index) => {
        // 각 센서마다 다른 색상과 애니메이션 지연
        const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3'];
        dot.style.background = colors[index];
        
        // 랜덤한 위치에서 시작
        const randomX = Math.random() * 20 - 10;
        const randomY = Math.random() * 20 - 10;
        dot.style.transform = `translate(${randomX}px, ${randomY}px)`;
        
        // 애니메이션 시작
        setTimeout(() => {
            dot.style.transition = 'all 0.5s ease';
            dot.style.transform = 'translate(0, 0)';
        }, index * 200);
    });
}

// 데모 시나리오 표시
function showScenario(scenarioNumber) {
    // 모든 시나리오 숨기기
    document.querySelectorAll('.scenario').forEach(scenario => {
        scenario.classList.remove('active');
    });
    
    // 모든 탭 버튼 비활성화
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 선택된 시나리오 표시
    const selectedScenario = document.getElementById(`scenario-${scenarioNumber}`);
    if (selectedScenario) {
        selectedScenario.classList.add('active');
    }
    
    // 선택된 탭 버튼 활성화
    const selectedBtn = document.querySelector(`.tab-btn:nth-child(${scenarioNumber})`);
    if (selectedBtn) {
        selectedBtn.classList.add('active');
    }
    
    // 시나리오별 특별한 애니메이션
    animateScenario(scenarioNumber);
}

// 시나리오별 애니메이션
function animateScenario(scenarioNumber) {
    const scenario = document.getElementById(`scenario-${scenarioNumber}`);
    if (!scenario) return;
    
    // 채팅 메시지 타이핑 효과
    const messageText = scenario.querySelector('.message-text');
    if (messageText) {
        const originalText = messageText.textContent;
        messageText.textContent = '';
        
        let i = 0;
        const typeWriter = () => {
            if (i < originalText.length) {
                messageText.textContent += originalText.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            }
        };
        
        setTimeout(typeWriter, 500);
    }
    
    // 데이터 값 애니메이션
    const dataValues = scenario.querySelectorAll('.data-value');
    dataValues.forEach((value, index) => {
        value.style.opacity = '0';
        value.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            value.style.transition = 'all 0.5s ease';
            value.style.opacity = '1';
            value.style.transform = 'translateY(0)';
        }, index * 100 + 200);
    });
}

// 대기자 등록 모달 열기
function openWaitlistModal() {
    const modal = document.getElementById('waitlistModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // 모달 열릴 때 애니메이션
        setTimeout(() => {
            modal.querySelector('.modal-content').style.transform = 'scale(1)';
        }, 10);
    }
}

// 대기자 등록 모달 닫기
function closeWaitlistModal() {
    const modal = document.getElementById('waitlistModal');
    if (modal) {
        modal.querySelector('.modal-content').style.transform = 'scale(0.9)';
        
        setTimeout(() => {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }, 300);
    }
}

// 모달 외부 클릭 시 닫기
window.addEventListener('click', function(event) {
    const modal = document.getElementById('waitlistModal');
    if (event.target === modal) {
        closeWaitlistModal();
    }
});

// 대기자 등록 폼 처리
function handleWaitlistSubmission(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const email = document.getElementById('email').value;
    const name = document.getElementById('name').value;
    const interest = document.getElementById('interest').value;
    
    // 간단한 유효성 검사
    if (!email || !name || !interest) {
        showNotification('모든 필드를 입력해주세요.', 'error');
        return;
    }
    
    if (!isValidEmail(email)) {
        showNotification('올바른 이메일 주소를 입력해주세요.', 'error');
        return;
    }
    
    // 실제로는 서버로 데이터를 전송해야 함
    // 여기서는 로컬 스토리지에 저장
    const waitlistData = {
        email: email,
        name: name,
        interest: interest,
        timestamp: new Date().toISOString()
    };
    
    // 기존 대기자 목록 가져오기
    let waitlist = JSON.parse(localStorage.getItem('plantiWaitlist') || '[]');
    waitlist.push(waitlistData);
    localStorage.setItem('plantiWaitlist', JSON.stringify(waitlist));
    
    // 성공 메시지 표시
    showNotification('대기자 등록이 완료되었습니다! 출시 소식을 가장 먼저 알려드릴게요.', 'success');
    
    // 폼 리셋
    e.target.reset();
    
    // 모달 닫기
    setTimeout(() => {
        closeWaitlistModal();
    }, 2000);
}

// 이메일 유효성 검사
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// 알림 표시
function showNotification(message, type = 'info') {
    // 기존 알림 제거
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    // 새 알림 생성
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // 스타일 추가
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4caf50' : type === 'error' ? '#f44336' : '#2196f3'};
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        z-index: 3000;
        animation: slideInRight 0.3s ease;
        max-width: 400px;
    `;
    
    // CSS 애니메이션 추가
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        .notification-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    // 3초 후 자동 제거
    setTimeout(() => {
        notification.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// 데모 섹션으로 스크롤
function scrollToDemo() {
    const demoSection = document.getElementById('demo');
    if (demoSection) {
        demoSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
        
        // 첫 번째 시나리오 자동 재생
        setTimeout(() => {
            showScenario(1);
        }, 1000);
    }
}

// 스크롤 애니메이션
function animateOnScroll() {
    const elements = document.querySelectorAll('.feature-card, .problem-card, .pricing-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    elements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'all 0.6s ease';
        observer.observe(element);
    });
}

// 페이지 로드 시 스크롤 애니메이션 초기화
document.addEventListener('DOMContentLoaded', function() {
    animateOnScroll();
});

// 식물 애니메이션 효과
function addPlantInteractions() {
    const plantContainer = document.querySelector('.plant-container');
    if (!plantContainer) return;
    
    plantContainer.addEventListener('mouseenter', function() {
        const leaves = document.querySelectorAll('.leaf');
        leaves.forEach(leaf => {
            leaf.style.animationPlayState = 'paused';
            leaf.style.transform = 'scale(1.1) rotate(5deg)';
        });
    });
    
    plantContainer.addEventListener('mouseleave', function() {
        const leaves = document.querySelectorAll('.leaf');
        leaves.forEach(leaf => {
            leaf.style.animationPlayState = 'running';
            leaf.style.transform = 'scale(1) rotate(0deg)';
        });
    });
}

// 페이지 로드 시 식물 인터랙션 초기화
document.addEventListener('DOMContentLoaded', function() {
    addPlantInteractions();
});

// 통계 카운터 애니메이션
function animateCounters() {
    const counters = document.querySelectorAll('.stat-number');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = counter.textContent;
                const isPercentage = target.includes('%');
                const isTime = target.includes('/');
                
                let finalValue = target;
                if (isPercentage) {
                    finalValue = '100%';
                } else if (isTime) {
                    finalValue = '24/7';
                } else {
                    finalValue = '6';
                }
                
                counter.textContent = '0';
                counter.style.transition = 'all 0.5s ease';
                
                setTimeout(() => {
                    counter.textContent = finalValue;
                }, 200);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => {
        observer.observe(counter);
    });
}

// 페이지 로드 시 카운터 애니메이션 초기화
document.addEventListener('DOMContentLoaded', function() {
    animateCounters();
});

// 키보드 접근성
document.addEventListener('keydown', function(e) {
    // ESC 키로 모달 닫기
    if (e.key === 'Escape') {
        closeWaitlistModal();
    }
    
    // Enter 키로 시나리오 전환 (탭 포커스 시)
    if (e.key === 'Enter' && e.target.classList.contains('tab-btn')) {
        const scenarioNumber = Array.from(document.querySelectorAll('.tab-btn')).indexOf(e.target) + 1;
        showScenario(scenarioNumber);
    }
});

// 터치 디바이스 지원
if ('ontouchstart' in window) {
    document.addEventListener('touchstart', function() {}, {passive: true});
}

// 성능 최적화: 디바운스 함수
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 스크롤 이벤트 최적화
const optimizedScrollHandler = debounce(function() {
    // 스크롤 관련 로직
}, 10);

window.addEventListener('scroll', optimizedScrollHandler);
