# Signalcraft Development Progress

## Current Architecture Structure

### JavaScript Directory Structure
```
static/js/
├── archived/                    # Archived JavaScript files
├── auth/                        # Authentication modules
│   ├── auth-manager.js          # Authentication management
│   └── kakao-oauth.js           # Kakao OAuth functionality
├── customer/                    # Customer dashboard modules
│   └── customer-dashboard.js    # Customer dashboard functionality
├── dashboard/                   # Main dashboard modules
│   ├── charts/                  # Chart-related modules
│   │   ├── anomaly-chart.js
│   │   ├── chart-manager.js
│   │   ├── device-status-chart.js
│   │   ├── energy-chart.js
│   │   ├── power-chart.js
│   │   ├── temperature-chart.js
│   │   └── vibration-chart.js
│   ├── data/                    # Data management modules
│   │   ├── api-client.js
│   │   └── data-loader.js
│   ├── ui/                      # UI management modules
│   │   ├── card-updater.js
│   │   ├── section-manager.js
│   │   └── table-renderer.js
│   └── utils/                   # Utility functions
│       ├── formatters.js
│       └── helpers.js
├── landing/                     # Landing page modules
│   ├── ai-diagnosis-demo.js     # AI diagnosis demo functionality
│   ├── ai-diagnosis.js          # AI diagnosis functionality
│   └── utils.js                 # Utility functions for landing page
├── mobile_app/                  # Mobile application modules
│   ├── charts/                  # Mobile chart modules
│   │   └── monitoring-chart.js
│   ├── data/                    # Mobile data modules
│   │   ├── api-client.js
│   │   ├── data-loader.js
│   │   └── offline-storage.js
│   ├── main-module.js           # Main module entry point
│   ├── pwa/                     # PWA-related modules
│   │   ├── notification-handler.js
│   │   └── pwa-manager.js
│   ├── sw.js                    # Service worker
│   ├── ui/                      # Mobile UI modules
│   │   ├── dashboard-updater.js
│   │   ├── navigation-manager.js
│   │   ├── notification-renderer.js
│   │   └── payment-renderer.js
│   └── utils/                   # Mobile utility functions
│       ├── formatters.js
│       └── helpers.js
├── notification_dashboard/      # Notification dashboard modules
│   ├── data/                    # Notification data modules
│   │   ├── api-client.js
│   │   └── data-loader.js
│   ├── forms/                   # Notification form modules
│   │   ├── notification-sender.js
│   │   ├── settings-manager.js
│   │   └── template-creator.js
│   ├── notification_dashboard.js # Entry point for notification dashboard
│   ├── ui/                      # Notification UI modules
│   │   ├── channel-renderer.js
│   │   ├── history-renderer.js
│   │   ├── overview-renderer.js
│   │   ├── tab-manager.js
│   │   └── template-renderer.js
│   └── utils/                   # Notification utility functions
│       ├── formatters.js
│       └── toast-manager.js
├── ui/                          # General UI modules
│   ├── modal-manager.js
│   ├── module-loader.js         # Dynamically loads HTML components
│   └── navbar-renderer.js
└── app.js                       # Main application entry point
```

### Template Directory Structure
```
templates/
├── admin/                       # Admin-related templates
├── customer/                    # Customer-specific templates
├── modules/                     # Reusable template modules
├── ai_demo.html                 # AI demonstration page
├── ai_models.html               # AI models page
├── ai_predict.html              # AI prediction page
├── ai_test.html                 # AI testing page
├── ai_training.html             # AI training page
├── ai_upload.html               # AI upload page
├── audio_recorder_client.html   # Audio recorder client page
├── base.html                    # Base template with customer dashboard script
├── base.htmly                   # Alternative base template with customer dashboard script
├── dashboard.html               # Main dashboard page
├── diagnosis_report.html        # Diagnosis report page
├── faq.html                     # FAQ page
├── home.html                    # Home page
├── login_success.html           # Login success page
├── login.html                   # Login page
├── marketing_landing_page.html  # Marketing landing page
├── mobile_app.html              # Mobile application page
├── notification_dashboard.html  # Notification dashboard page
├── pricing.html                 # Pricing page
└── showcase.html                # Showcase page
```

### Static Component Directory Structure
```
static/landing-components/
├── demo.html                    # AI diagnosis demo section
├── features/                    # Detailed feature sub-components
│   ├── ai-analysis.html         # AI analysis feature
│   ├── monitoring.html          # 24/7 monitoring feature
│   ├── notifications.html       # Multi-channel notifications feature
│   ├── mobile-access.html       # Mobile application access
│   └── integrations.html        # System integrations
├── features.html                # Features section
├── footer.html                  # Footer section
├── header.html                  # Header section with mobile navigation
├── hero.html                    # Hero section with full-width video
└── pricing.html                 # Pricing section
```

## Add New Files

### Instructions
To add a new file to the architecture:

1. Determine which functional module the file belongs to
2. Place the file in the appropriate subdirectory
3. Update this document to reflect the new file
4. Update any HTML templates that need to reference the new file
5. Add the file to the appropriate build or import process if needed

## Remove Files

### Instructions
To remove a file from the architecture:

1. Verify that the file is not referenced in any HTML templates
2. Update HTML templates to remove references to the file
3. Update this document to remove references to the file
4. Consider archiving instead of deleting to preserve for potential future use
5. Delete the file if sure it's no longer needed

## Modify Files

### Instructions
To modify an existing file:

1. Update the file with the required changes
2. Verify that functionality remains intact
3. Update this document if the file's purpose or location changes
4. Update any dependent files that might be affected
5. Update HTML templates if the modification affects how the file is referenced

---

## 2025-10-13: Mobile Navigation Implementation

### Objective
Implement responsive mobile navigation with a hamburger menu in the top right corner that appears on small screens.

### Changes Made
- **Updated HTML Structure** (`static/landing-components/header.html`):
  - Added hamburger menu button with three bars in the top right corner
  - Created mobile navigation panel that slides in from the right
  - Included close button for easy dismissal
  - Maintained all original navigation links in the mobile menu

- **Added CSS Styles** (`static/css/landing.css`):
  - Implemented hamburger menu toggle button with animated bars
  - Created mobile navigation panel with smooth slide-in animation
  - Added media query to show mobile menu only on screens smaller than 768px
  - Maintained consistent styling with the rest of the application

- **Enhanced JavaScript Functionality** (`static/js/landing/utils.js`):
  - Added robust initialization function that handles dynamically loaded content
  - Implemented hamburger menu toggle functionality
  - Added mobile menu closing on outside clicks and link selections
  - Used interval-based approach to handle timing issues with dynamic content loading

### Benefits
- Improved mobile user experience with accessible navigation
- Maintained responsive design principles
- Ensured consistent functionality across different screen sizes
- Fixed timing issues with dynamically loaded header components

---

## 2025-10-13: Text Readability Improvements

### Objective
Enhance text readability by implementing strategic line breaks in feature descriptions across various components.

### Changes Made
- **Features Section** (`static/landing-components/features.html`):
  - Added line breaks in "AI 음성 분석" description: "냉동고의 미세한 소리 변화를", "AI가 실시간으로 분석하여", and "고장 징후를 99.9% 정확도로 감지합니다."
  - Added line breaks in "24시간 모니터링" description: "매장 운영 시간에 구애받지 않고,", "24시간 내내 클라우드 기반으로", and "냉동고 상태를 확인합니다."
  - Added line breaks in "즉시 알림" description: "문제 발생 시 즉시 설정된 담당자에게", "전화, 문자, 앱 푸시 등", and "다양한 채널로 알림을 전송합니다."

- **Feature-Specific Components**:
  - **Monitoring** (`static/landing-components/features/monitoring.html`): Added line breaks: "상점 운영 시간에 구애받지 않고," and "24시간 내내 냉동고 상태를 지속적으로"
  - **Notifications** (`static/landing-components/features/notifications.html`): Added line breaks: "이상 징후가 감지되면" and "이메일, 문자(SMS), 카카오톡 등 다양한 방식으로"
  - **Mobile Access** (`static/landing-components/features/mobile-access.html`): Added line breaks: "모바일 앱을 통해 언제 어디서든" and "냉동고 상태를 실시간으로 확인하고"

### Benefits
- Improved readability with better text flow
- Enhanced user experience through visual text separation
- Better comprehension of feature descriptions
- Maintained consistent design language across components

---

## 2025-10-13: Full-Width Hero Section Implementation

### Objective
Create a more immersive hero section by making the video span the full width of the screen.

### Changes Made
- **CSS Updates** (`static/css/landing.css`):
  - Made hero section span full viewport width with `width: 100vw` and `margin-left: calc(50% - 50vw)`
  - Adjusted video container to span full width with `width: 100vw`
  - Updated video styling with `object-fit: cover` and `max-height: 100vh`
  - Enhanced text positioning with proper z-index and container adjustments

- **HTML Structure Update** (`static/landing-components/hero.html`):
  - Separated video container from text content for better layout control
  - Maintained existing text content and structure
  - Kept proper semantic structure and accessibility

- **Text Readability Enhancement**:
  - Added explicit line break in hero subtitle: "AI 기술로 냉동고를 24시간 모니터링하고, 문제를 미리 감지하여" and "매장을 지켜드립니다."

### Benefits
- More immersive and visually impactful hero section
- Better video display with full-width coverage
- Improved user engagement through visual presence
- Enhanced readability with text line breaks
- Better mobile responsiveness

---

## 2025-10-13: Centralized Text Alignment

### Objective
Improve visual consistency by centering text and elements in key sections.

### Changes Made
- **Features Section** (`static/css/landing.css`):
  - Added `text-align: center` to `.features` class
  - Centered feature cards grid with `margin: 0 auto`
  - Added `justify-content: center` and `align-items: center` for grid items
  - Centered content inside feature cards with `align-items: center`

- **Hero Section** (`static/css/landing.css`):
  - Added `text-align: center` to `.hero` class for proper text alignment

### Benefits
- Improved visual balance and consistency
- Better readability with centered content
- Enhanced user experience with symmetrical design
- Maintained responsive layout