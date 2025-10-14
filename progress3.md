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
Template Directory Structure
templates/
├── admin/                       # Admin-related templates
│   ├── ai_dashboard.html        # AI dashboard page
│   ├── ai_demo.html             # AI demonstration page
│   ├── ai_models.html           # AI models page
│   ├── ai_predict.html          # AI prediction page
│   ├── ai_test.html             # AI testing page
│   ├── ai_training.html         # AI training page
│   ├── ai_upload.html           # AI upload page
│   ├── analytics.html           # Analytics page
│   ├── base_admin.html          # Admin base template
│   ├── base.html                # Alternative base template for admin
│   ├── customers.html           # Customer management page
│   ├── dashboard.html           # Admin dashboard page
│   ├── freezers.html            # Freezer management page
│   └── ml_management.html       # ML model management page
├── customer/                    # Customer-specific templates
│   ├── audio_recorder_client.html # Audio recorder client page
│   ├── contact.html             # Contact page
│   ├── dashboard.html           # Customer dashboard page
│   ├── diagnosis_report.html    # Diagnosis report page
│   ├── login_success.html       # Login success page
│   ├── marketing_landing_page.html # Marketing landing page
│   ├── mobile_app.html          # Mobile application page
│   └── notification_dashboard.html # Notification dashboard page
├── modules/                     # Reusable template modules
│   └── customer_dashboard.html  # Reusable customer dashboard component
├── base.html                    # Base template with customer dashboard script
├── faq.html                     # FAQ page
├── home.html                    # Home page
├── index.html                   # Main index/landing page
├── login.html                   # Login page
├── pricing.html                 # Pricing page
└── showcase.html                # Showcase page
Static Component Directory Structure
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
Add New Files
Instructions
To add a new file to the architecture:

Determine which functional module the file belongs to
Place the file in the appropriate subdirectory
Update this document to reflect the new file
Update any HTML templates that need to reference the new file
Add the file to the appropriate build or import process if needed
Remove Files
Instructions
To remove a file from the architecture:

Verify that the file is not referenced in any HTML templates
Update HTML templates to remove references to the file
Update this document to remove references to the file
Consider archiving instead of deleting to preserve for potential future use
Delete the file if sure it's no longer needed
Modify Files
Instructions
To modify an existing file:

Update the file with the required changes
Verify that functionality remains intact
Update this document if the file's purpose or location changes
Update any dependent files that might be affected
Update HTML templates if the modification affects how the file is referenced
2025-10-13: Mobile Navigation Implementation
Objective
Implement responsive mobile navigation with a hamburger menu in the top right corner that appears on small screens.

Changes Made
Updated HTML Structure (static/landing-components/header.html):

Added hamburger menu button with three bars in the top right corner
Created mobile navigation panel that slides in from the right
Included close button for easy dismissal
Maintained all original navigation links in the mobile menu
Added CSS Styles (static/css/landing.css):

Implemented hamburger menu toggle button with animated bars
Created mobile navigation panel with smooth slide-in animation
Added media query to show mobile menu only on screens smaller than 768px
Maintained consistent styling with the rest of the application
Enhanced JavaScript Functionality (static/js/landing/utils.js):

Added robust initialization function that handles dynamically loaded content
Implemented hamburger menu toggle functionality
Added mobile menu closing on outside clicks and link selections
Used interval-based approach to handle timing issues with dynamic content loading
Benefits
Improved mobile user experience with accessible navigation
Maintained responsive design principles
Ensured consistent functionality across different screen sizes
Fixed timing issues with dynamically loaded header components
2025-10-13: Text Readability Improvements
Objective
Enhance text readability by implementing strategic line breaks in feature descriptions across various components.

Changes Made
Features Section (static/landing-components/features.html):

Added line breaks in "AI 음성 분석" description: "냉동고의 미세한 소리 변화를", "AI가 실시간으로 분석하여", and "고장 징후를 99.9% 정확도로 감지합니다."
Added line breaks in "24시간 모니터링" description: "매장 운영 시간에 구애받지 않고,", "24시간 내내 클라우드 기반으로", and "냉동고 상태를 확인합니다."
Added line breaks in "즉시 알림" description: "문제 발생 시 즉시 설정된 담당자에게", "전화, 문자, 앱 푸시 등", and "다양한 채널로 알림을 전송합니다."
Feature-Specific Components:

Monitoring (static/landing-components/features/monitoring.html): Added line breaks: "상점 운영 시간에 구애받지 않고," and "24시간 내내 냉동고 상태를 지속적으로"
Notifications (static/landing-components/features/notifications.html): Added line breaks: "이상 징후가 감지되면" and "이메일, 문자(SMS), 카카오톡 등 다양한 방식으로"
Mobile Access (static/landing-components/features/mobile-access.html): Added line breaks: "모바일 앱을 통해 언제 어디서든" and "냉동고 상태를 실시간으로 확인하고"
Benefits
Improved readability with better text flow
Enhanced user experience through visual text separation
Better comprehension of feature descriptions
Maintained consistent design language across components
2025-10-13: Full-Width Hero Section Implementation
Objective
Create a more immersive hero section by making the video span the full width of the screen.

Changes Made
CSS Updates (static/css/landing.css):

Made hero section span full viewport width with width: 100vw and margin-left: calc(50% - 50vw)
Adjusted video container to span full width with width: 100vw
Updated video styling with object-fit: cover and max-height: 100vh
Enhanced text positioning with proper z-index and container adjustments
HTML Structure Update (static/landing-components/hero.html):

Separated video container from text content for better layout control
Maintained existing text content and structure
Kept proper semantic structure and accessibility
Text Readability Enhancement:

Added explicit line break in hero subtitle: "AI 기술로 냉동고를 24시간 모니터링하고, 문제를 미리 감지하여" and "매장을 지켜드립니다."
Benefits
More immersive and visually impactful hero section
Better video display with full-width coverage
Improved user engagement through visual presence
Enhanced readability with text line breaks
Better mobile responsiveness
2025-10-13: Centralized Text Alignment
Objective
Improve visual consistency by centering text and elements in key sections.

Changes Made
Features Section (static/css/landing.css):

Added text-align: center to .features class
Centered feature cards grid with margin: 0 auto
Added justify-content: center and align-items: center for grid items
Centered content inside feature cards with align-items: center
Hero Section (static/css/landing.css):

Added text-align: center to .hero class for proper text alignment
Benefits
Improved visual balance and consistency
Better readability with centered content
Enhanced user experience with symmetrical design
Maintained responsive layout
2025-10-13: Comprehensive Login System Implementation
Objective
Implement a complete login system with multiple authentication options, registration, and password recovery functionality.

Changes Made
Enhanced Login Modal (static/js/ui/modal-manager.js):

Added OAuth login options (Kakao, Google)
Implemented comprehensive email/password login
Added "Remember me" functionality
Created password recovery flow
Implemented proper form validation
Enhanced Registration Modal (static/js/ui/modal-manager.js):

Added detailed registration form with name fields
Implemented password confirmation validation
Added optional phone and company fields
Added terms of service and marketing consent checkboxes
Password Recovery Modal (static/pages/index.html):

Created dedicated modal for password reset
Added email validation for reset requests
Script Loading Order (static/pages/index.html):

Reordered script loading to ensure class dependencies are met
Added proper loading sequence for AuthManager, KakaoOAuth, NavbarRenderer, and ModalManager
Added Bootstrap and jQuery dependencies
Robust Initialization (static/app.js):

Implemented safety checks for class existence before instantiation
Added error handling for missing classes
Created conditional execution for manager-dependent functions
Added custom event dispatch for initialization completion
Module Loader Synchronization (static/js/ui/module-loader.js):

Added wait mechanism for managers to initialize before loading components
Implemented polling approach with safety timeout
Ensured header component loads only after managers are ready
Global Function Enhancements (static/app.js):

Updated all global functions with safety checks
Added fallback mechanisms for uninitialized managers
Implemented timeout-based retry logic
Benefits
Complete authentication flow with multiple options (OAuth, email/password)
Improved user experience with comprehensive forms and validation
Robust error handling and initialization order
Proper script loading sequence preventing "class not defined" errors
Enhanced security with proper form validation and OAuth integration
Better user guidance with appropriate messaging throughout the flow
2025-10-13: Login Modal Component Refinement
Objective
Improve the login modal with dark mode styling, logo consistency, proper sizing, and error handling.

Changes Made
Dark Mode Styling (static/landing-components/login-modal.html, static/landing-components/register-modal.html):

Applied dark background with light text throughout modal components
Changed primary buttons to light buttons with dark text for contrast
Updated form elements to match dark theme with appropriate contrast
Logo Background Consistency (static/landing-components/login-modal.html, static/landing-components/register-modal.html):

Added circular background area around logo matching the landing page header background
Used consistent #000000 background to maintain visual consistency between landing page and modals
Modal Sizing Improvements (static/landing-components/login-modal.html, static/landing-components/register-modal.html):

Reduced login modal size from default to modal-sm for better UX
Changed registration modal from modal-lg to default size to prevent overwhelming users
Error Handling Enhancement (static/js/ui/modal-manager.js):

Added checks to verify function existence before attaching event listeners
Implemented proper response status checking during modal loading
Added console warnings for missing functions instead of throwing errors
Showcase Page Integration (templates/showcase.html):

Added login button to showcase page header
Implemented modal loading functionality for both login and registration modals
Maintained all authentication features in showcase page context
Benefits
Enhanced visual consistency with landing page header through consistent logo styling
Improved user experience with appropriately sized modals
Better error handling preventing console errors when functions are not available
Consistent dark mode design language across both authentication modals
Seamless integration of authentication modals in both landing and showcase pages
2025-10-14: Template Directory Restructure and Cleanup
Objective
Organize and clean up template files according to the architecture specification with proper categorization.

Changes Made
Removed Duplicate Files:

Deleted base.htmly (duplicate of base.html with missing auth manager script)
Deleted index.html.backup (backup file)
Reorganized Templates by Function:

Admin Templates: Moved all AI-related files (ai_demo.html, ai_models.html, ai_predict.html, ai_test.html, ai_training.html, ai_upload.html) to admin/ directory
Customer Templates: Moved customer-facing pages (dashboard.html, diagnosis_report.html, mobile_app.html, notification_dashboard.html, login_success.html, audio_recorder_client.html, marketing_landing_page.html) to customer/ directory
Preserved Main Templates: Kept general landing pages (home.html, index.html, login.html, pricing.html, showcase.html) in main templates directory as they serve broader purposes
Updated Architecture Documentation:

Updated the Template Directory Structure section in progress3.md to reflect the new organization
Maintained clear separation between admin, customer, and module templates
Benefits
Improved maintainability with clean separation of concerns
Reduced code duplication and redundancy
Clearer architecture following specified directory structure
Easier navigation and file management for development team


# Progress Report 3: Enhanced Security for Showcase Page

## Objective
The primary goal was to secure the `/showcase` page and its associated assets, restricting access to authorized administrators only. This prevents general users from viewing internal or sensitive content.

## Analysis & Discovery
1.  **Target Identification**: The main page to be protected was identified as `/showcase`, which serves `static/pages/showcase.html`. A critical related asset, `/static/js/enhanced-registration.js`, was also identified as requiring protection.
2.  **Authentication Mechanism**: We analyzed the existing authentication flow and discovered the `authenticateSession` middleware within `server/routes/authRoutes.js`. This middleware validates users based on a `sessionId` cookie stored in the browser.
3.  **Role-Based Access Control (RBAC)**: The session data, populated by the middleware, was found to contain a `role` property for each user. This discovery was key to implementing fine-grained access control.

## Implementation Details
All modifications were applied directly to `server/app.js` to centralize the new security logic without major refactoring:

1.  **Middleware Implementation**:
    *   A `verifySession` middleware was added to `app.js`, replicating the logic from `authRoutes.js`. This function checks for a valid session cookie and attaches user data to the `req` object. Unauthorized users are redirected to the home page.
    *   A second middleware, `ensureAdmin`, was created to check if the `req.user.role` property is equal to `'admin'`. If the user is not an administrator, a `403 Forbidden` error is returned.

2.  **Route Protection**:
    *   The middleware chain `[verifySession, ensureAdmin]` was applied to the existing `app.get('/showcase', ...)` route.
    *   A new, specific route was created to protect the JavaScript asset: `app.get('/static/js/enhanced-registration.js', [verifySession, ensureAdmin], ...)`. This route was strategically placed before the generic `express.static` middleware to ensure it correctly intercepts requests for that specific file.

## Outcome
The `/showcase` page and its related JavaScript file are now fully protected. Only users who are logged in as administrators can access these resources. This change enhances the application's security by enforcing proper authorization on internal-facing pages.

---

### 2025-10-14: AI Diagnosis Component UX Refinement & Bug Fix

**Objective:**
To modularize the AI Diagnosis feature, improve the user experience of the demo component, and fix a bug preventing its use.

**Changes Made:**

1.  **Component Modularization:**
    *   The AI diagnosis logic, originally embedded in `templates/index.html`, was extracted.
    *   The JavaScript logic was consolidated into the existing, preferred file: `static/js/landing/ai-diagnosis.js`.
    *   Required CSS styles for result display were moved from `index.html` and appended to `static/css/landing.css`.
    *   The `static/landing-components/demo.html` file was converted into a standalone, functional HTML document by linking the appropriate CSS and JS files.

2.  **UX Refinement (Button Swapping):**
    *   The initial UI now only shows the "Start Recording" button.
    *   Upon successful recording, the "Start Recording" button is hidden and replaced by the "Diagnose" button.
    *   After the diagnosis result is displayed, the UI resets, hiding the "Diagnose" button and showing the "Start Recording" button again, creating an intuitive loop for the user.

3.  **Bug Fix (Disabled Button):**
    *   Fixed a bug where the "Start Recording" button remained disabled on supported browsers. The `checkBrowserSupport` function in `ai-diagnosis.js` was updated to explicitly enable the button.

**Benefits:**
*   The AI Diagnosis feature is now a reusable, self-contained component.
*   The user flow is more intuitive and less cluttered.
*   The component is now fully functional and robust.

---

### 2025-10-14: Footer Refinement and Legal Page Implementation

**Objective:**
To enhance the website's footer, create dedicated pages for the Terms of Service and Privacy Policy, and ensure a consistent user experience and design across all pages, including a functional dark mode and proper navigation.

**Changes Made:**

1.  **Footer Component Refinement (`footer.html`):**
    *   The footer was restructured into a professional 3-column layout:
        *   **Column 1:** Contains a brief company description and copyright notice.
        *   **Column 2:** Features "Quick Links" (Home, Features, Pricing, Demo) for easy navigation.
        *   **Column 3:** Includes links to legal pages and contact information.
    *   This change was made directly in `static/landing-components/footer.html` to improve site-wide information accessibility.

2.  **Legal Page Architecture Overhaul:**
    *   **Initial Approach (Standalone Pages):** Initially, `terms.html` and `privacy.html` were created as standalone HTML files. This led to several issues:
        *   The sticky header overlapped the content.
        *   Dark mode was not applied correctly.
        *   Footer navigation links were broken.
    *   **Revised Approach (Template-based):** To solve these inconsistencies, the architecture was refactored to mirror the main landing page (`static/pages/index.html`).
        *   A new template, `static/pages/legal.html`, was created. This template loads all the same CSS and JavaScript files as the main landing page, ensuring a consistent environment.
        *   `terms.html` and `privacy.html` were converted into content-only components, which are dynamically loaded into the `legal.html` template.
        *   The Express server (`server/app.js`) was updated to serve `legal.html` for both the `/terms` and `/privacy` routes.

3.  **CSS and JavaScript Enhancements:**
    *   **Styling:** A new `.legal-container` CSS class was added to `landing.css` to style the legal text for readability in dark mode.
    *   **Dynamic Link Correction:** A JavaScript snippet was added to `legal.html` to dynamically fix the footer's "Quick Links". It prepends a `/` to the `href` attributes (e.g., `href="#features"` becomes `href="/#features"`), ensuring they correctly navigate back to the main landing page sections from the legal pages.

**Benefits:**
*   **Consistent UX/UI:** The legal pages now share the exact same look, feel, and behavior as the main landing page, including the header, footer, and dark mode.
*   **Improved Navigation:** All navigation links, including the footer's "Quick Links", are now fully functional across the entire site.
*   **Maintainable Architecture:** The template-based approach is more robust and easier to maintain, as the header and footer are shared components, and styling is centralized in `landing.css`.
*   **Professionalism:** The site now includes standard, accessible legal pages and a more informative footer, increasing user trust.