# Signalcraft Development Progress

## Date: October 12, 2025

## Frontend Architecture Structure

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
├── app.js                       # Main application entry point
└── ... (other legacy files moved to archived/)
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
├── features.html                # Features section
├── footer.html                  # Footer section
├── header.html                  # Header section
├── hero.html                    # Hero section
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

### 2025-10-13: Landing Page Refactoring & Modularization

- **Objective:** Overhaul the landing page to align with a minimalist, conversion-focused design inspired by `busy.bar`.
- **Changes:**
    - **Modularized HTML:** Decomposed the monolithic `index.html` into smaller, reusable components located in `static/landing-components/`. Modules include `header`, `hero`, `features`, `demo`, `pricing`, and `footer`.
    - **Dynamic Loading:** Implemented `static/js/ui/module-loader.js` to asynchronously load and inject HTML components into the main page skeleton, improving maintainability.
    - **CSS Overhaul:** Completely rewrote `static/css/landing.css` from scratch. Removed Bootstrap dependency in favor of a custom, minimalist dark-theme stylesheet using modern CSS (Flexbox, Grid, CSS variables).
    - **Bug Fix (Race Condition):** Resolved an issue where the `ai-diagnosis.js` script would fail to initialize. The script now initializes via a callback from the `module-loader` only after its required HTML (`demo.html`) is fully loaded into the DOM.
- **Next Steps:** Address backend API connectivity issue for the "Analyze" functionality.

---

### 2025-10-13: Landing Page Features Enhancement

- **Objective:** Expand the features section with detailed, alternating layout design inspired by `busy.bar`, implementing modular sub-components for maintainability.
- **Changes:**
    - **New Sub-components:** Created modular feature sub-components in `static/landing-components/features/` directory:
        - `ai-analysis.html` - Detailed AI analysis feature
        - `monitoring.html` - 24/7 monitoring feature
        - `notifications.html` - Multi-channel notifications feature
        - `mobile-access.html` - Mobile application access
        - `integrations.html` - System integrations
    - **Alternating Layout:** Implemented alternating left/right content layout with alternating dark/light background sections for visual interest and engagement.
    - **Updated Module Loader:** Modified `static/js/ui/module-loader.js` to load the new detailed feature components after the main features section.
    - **Enhanced CSS:** Added new CSS rules in `static/css/landing.css` for:
        - Alternating layout patterns using `flex-direction: row` and `flex-direction: row-reverse`
        - Dark/light mode backgrounds for feature sections
        - Improved typography and spacing for detailed feature content
        - Responsive design for all screen sizes
    - **Modular Architecture:** Maintained the component-based architecture while adding detailed feature sections without bloating the main features.html component.
- **Benefits:**
    - **Improved User Engagement:** Alternating layout pattern follows best practices from reference site `busy.bar` to reduce visual monotony
    - **Better Content Organization:** Complex features explained in dedicated sections while maintaining overview at the top
    - **Enhanced Maintainability:** Sub-components can be updated independently without affecting the main features section
    - **Visual Appeal:** Dark/light mode alternation and left/right content flow improves user experience

---

### 2025-10-13: Feature Cards Styling Update

- **Objective:** Enhance the visual design of the main features section by styling the three feature items as interactive cards with improved spacing.
- **Changes:**
    - **Updated HTML Structure:** Changed from `feature-item` to `feature-card` elements in `static/landing-components/features.html`
    - **Increased Heading Padding:** Added more padding below the "왜 Signalcraft인가?" heading (48px)
    - **Added Card Styling:** Implemented card-based styling with hover effects, consistent padding, and visual depth
    - **Enhanced Interactions:** Added hover effects with slight elevation and shadow for better user experience
    - **Improved Layout:** Added consistent spacing between cards and better vertical rhythm
- **Benefits:**
    - **Better Visual Hierarchy:** Increased padding below the heading clearly separates it from the feature cards
    - **Enhanced Interactivity:** Hover effects provide visual feedback to users
    - **Modern Design:** Card-based layout follows contemporary design practices
    - **Improved Readability:** Consistent spacing and styling enhances content consumption

---

### 2025-10-13: Hero Section Video Integration

- **Objective:** Enhance the hero section by adding a video to better demonstrate the product functionality.
- **Changes:**
    - **Created Video Directory:** Created `static/videos/` directory to store video assets
    - **Updated Hero Component:** Modified `static/landing-components/hero.html` to include video element with autoplay, muted, and loop attributes
    - **Enhanced CSS Styling:** Added styles in `static/css/landing.css` for video container with proper spacing, borders, and shadow effects
    - **Maintained Text Separation:** Kept text content separate from video for better readability and visual hierarchy
    - **Responsive Design:** Ensured video scales appropriately on different screen sizes
- **Benefits:**
    - **Improved Engagement:** Video content captures user attention and better demonstrates product value
    - **Better Content Hierarchy:** Separation of text and video maintains readability while adding visual interest
    - **Professional Appearance:** Styled video container with borders and shadows adds visual depth
    - **Optimized Performance:** Using autoplay with muted attribute ensures smooth playback without user interaction

---

### 2025-10-13: Hero Section Video Positioning and Sizing

- **Objective:** Position the video at the top of the hero section, make it as wide as the features section, and ensure proper layout order (video first, then text).
- **Changes:**
    - **Updated HTML Structure:** Reordered content in `static/landing-components/hero.html` so video appears before text content
    - **Adjusted Video Width:** Set video container width to match the features section (1100px max-width)
    - **Enhanced Centering:** Ensured video is properly centered within the container
    - **Increased Top Space:** Added increased top padding to the hero section to make it more visually prominent
    - **Improved Spacing:** Added more space between video and text content for better visual hierarchy
- **Benefits:**
    - **Better Visual Hierarchy:** Video now appears first and draws attention immediately upon page load
    - **Consistent Width:** Video now matches the width of the features section for visual consistency
    - **Improved Layout:** Proper positioning and spacing create a more polished look
    - **Enhanced Attention:** Increased top padding and video positioning ensure the hero section draws user attention

---

### Completed: Common Utilities Integration

#### Overview
Successfully completed the integration of common utilities across multiple modules to reduce code duplication and improve maintainability.

#### Tasks Completed

1. **Created directory structure**: `static/js/common/` and `static/js/common/utils/`
2. **Created common utility files**:
   - `static/js/common/utils/formatters.js` - Consolidates all formatting functions from various modules
   - `static/js/common/utils/helpers.js` - Consolidates all helper functions from various modules
   - `static/js/common/index.js` - Main export file for all common utilities
3. **Integrated common utilities into existing modules**:
   - Updated `static/js/dashboard/` modules to import from common utilities
   - Updated `static/js/notification_dashboard/` modules to import from common utilities
   - Updated `static/js/mobile_app/` modules to import from common utilities
4. **Ensured backward compatibility**:
   - Maintained global window function registrations where required
   - Updated import statements to use aliases and avoid naming conflicts
5. **Updated all referencing modules**:
   - Updated UI modules (table-renderer.js, channel-renderer.js, etc.) to use imported functions
   - Ensured all modules that previously had duplicated functions now use the common ones

#### Functions Consolidated

**Formatters Module:**
- `formatDate` - Formats dates in Korean format (from dashboard utils)
- `formatDateTime` - Formats dates with fallback (from notification_dashboard utils)
- `formatTime` - Formats relative time (from mobile_app utils)
- `getStatusText` - Maps status codes to display text
- `getStatusClass` - Maps status codes to CSS classes
- `getPriorityClass` - Maps priority levels to CSS classes
- `getHealthClass` - Maps health scores to CSS classes
- `getTypeColor` - Maps notification types to color classes
- `getTypeDisplayName` - Maps notification types to display names
- `getPriorityColor` - Maps priority levels to color classes
- `getChannelIcon` - Maps channel names to icon classes
- `getChannelDisplayName` - Maps channel names to display names

**Helpers Module:**
- `showAlert` - Shows alert messages (from dashboard utils)
- `showToast` - Shows toast notifications (from notification_dashboard utils)
- `startAutoRefreshHelper` - Starts auto-refresh intervals (from dashboard utils)
- `stopAutoRefreshHelper` - Stops auto-refresh intervals (from dashboard utils)
- `openModal` - Opens Bootstrap modals (from dashboard utils)
- `closeModal` - Closes Bootstrap modals (from dashboard utils)
- `handleOnlineStatus` - Handles online/offline status changes (from mobile_app utils)
- `showOfflineModal` - Shows offline modals (from mobile_app utils)

#### Benefits Achieved

- **Reduced code duplication**: Eliminated duplicate utility functions across modules
- **Improved maintainability**: Common functions are now maintained in a single location
- **Enhanced consistency**: All modules now use identical utility functions
- **Easier updates**: Changes to common utilities automatically propagate to all modules
- **Better organization**: Related utility functions are grouped in a dedicated common directory
- **Maintained compatibility**: All existing functionality preserved with backward compatibility

#### Files Created/Modified

1. `static/js/common/utils/formatters.js` - Common formatting functions
2. `static/js/common/utils/helpers.js` - Common helper functions
3. `static/js/common/index.js` - Aggregated exports for common utilities
4. Updated all dashboard module utility files to import from common
5. Updated all notification_dashboard module utility files to import from common
6. Updated all mobile_app module utility files to import from common
7. Updated dependent UI modules to use imported functions

#### Verification
All functionality remains intact after integration. All modules correctly import and use the common utilities, and no regressions were introduced. The application works exactly as before but with a more maintainable code structure following the principle of single source of truth for common utilities.

---

### Completed: Frontend Modularization

#### Overview
Successfully completed the modularization of the landing page (index.html) as outlined in the sw.md document.

#### Tasks Completed

1. **Created directory structure**: `static/js/landing/`
2. **Created external JavaScript files**:
   - `static/js/landing/ai-diagnosis.js` - Contains the `IntegratedAIDiagnosis` class with all its methods
   - `static/js/landing/utils.js` - Contains utility functions for smooth scrolling and plan selection
3. **Created external CSS file**: `static/css/landing.css` containing all the CSS styles from the original index.html
4. **Updated index.html**:
   - Removed all inline CSS and replaced with a link to `/static/css/landing.css`
   - Removed all inline JavaScript and replaced with links to external files:
     - `/static/js/landing/utils.js`
     - `/static/js/landing/ai-diagnosis.js`

#### Benefits Achieved

- **Reduced index.html size**: The main HTML file is now much cleaner and more maintainable
- **Better organization**: JavaScript and CSS are now in dedicated files following proper separation of concerns
- **Improved maintainability**: Each component is in its own file, making it easier to update and debug
- **Reusability**: The JavaScript modules can now be reused in other parts of the application if needed
- **Performance**: Browsers can cache external CSS and JS files, potentially improving load times on subsequent visits

#### Files Created/Modified

1. `static/js/landing/ai-diagnosis.js` - Contains the AI diagnosis functionality
2. `static/js/landing/utils.js` - Contains utility functions for scrolling and plan selection
3. `static/css/landing.css` - Contains all the original CSS styles
4. `static/index.html` - Updated to reference external CSS and JS files

#### Verification
All functionality remains intact after modularization. The landing page works exactly as before but with a much cleaner, more maintainable code structure.

---

### Completed: App.js Modularization

#### Overview
Successfully completed the modularization of the main `app.js` file as outlined in the updated sw.md document.

#### Tasks Completed

1. **Created directory structure**: `static/js/auth/` and `static/js/ui/`
2. **Created authentication modules**:
   - `static/js/auth/auth-manager.js` - Handles authentication logic (login, logout, status management)
   - `static/js/auth/kakao-oauth.js` - Handles Kakao OAuth functionality
3. **Created UI modules**:
   - `static/js/ui/navbar-renderer.js` - Manages navigation UI and user interface rendering
   - `static/js/ui/modal-manager.js` - Handles modal dialogs (login, registration)
4. **Simplified main `app.js`**:
   - Reduced from ~800+ lines to ~100 lines focused on initialization
   - Maintained backward compatibility with existing HTML files
5. **Updated HTML files** to reference the new module files:
   - `static/index.html`
   - `templates/index.html`
   - `templates/marketing_landing_page.html`

#### Benefits Achieved

- **Reduced app.js size**: Main app.js file is significantly smaller and focused only on initialization
- **Better organization**: Specific functionality is now organized into dedicated modules
- **Improved maintainability**: Each component is in its own file, making it easier to update and debug
- **Enhanced reusability**: Modules can be more easily reused across different pages
- **Maintained compatibility**: All existing functionality preserved with backward compatibility

#### Files Created/Modified

1. `static/js/auth/auth-manager.js` - Authentication management
2. `static/js/auth/kakao-oauth.js` - Kakao authentication
3. `static/js/ui/navbar-renderer.js` - Navigation rendering
4. `static/js/ui/modal-manager.js` - Modal management
5. `static/app.js` - Simplified entry point
6. Updated HTML files to reference new modules

#### Verification
All functionality remains intact after modularization. The application works exactly as before but with a much cleaner, more maintainable code structure.

---

### Completed: Dashboard.js Modularization

#### Overview
Successfully completed the modularization of the main `dashboard.js` file as outlined in the sw.md document.

#### Tasks Completed

1. **Created directory structure**: `static/js/dashboard/` with subdirectories for charts, data, ui, and utils
2. **Created chart modules**:
   - `static/js/dashboard/charts/chart-manager.js` - Manages all charts
   - `static/js/dashboard/charts/energy-chart.js` - Energy consumption chart
   - `static/js/dashboard/charts/device-status-chart.js` - Device status doughnut chart
   - `static/js/dashboard/charts/temperature-chart.js` - Temperature trend chart
   - `static/js/dashboard/charts/vibration-chart.js` - Vibration analysis chart
   - `static/js/dashboard/charts/power-chart.js` - Power consumption pattern chart
   - `static/js/dashboard/charts/anomaly-chart.js` - Anomaly detection chart
3. **Created data modules**:
   - `static/js/dashboard/data/api-client.js` - Handles API calls
   - `static/js/dashboard/data/data-loader.js` - Manages data loading operations
4. **Created UI modules**:
   - `static/js/dashboard/ui/table-renderer.js` - Updates all data tables
   - `static/js/dashboard/ui/section-manager.js` - Handles section navigation and content loading
   - `static/js/dashboard/ui/card-updater.js` - Updates overview cards
5. **Created utility modules**:
   - `static/js/dashboard/utils/formatters.js` - Contains formatting functions (date, status, etc.)
   - `static/js/dashboard/utils/helpers.js` - Contains helper functions (alerts, modals, etc.)
6. **Simplified main `dashboard.js`**:
   - Reduced from ~847 lines to ~200 lines focused on initialization and coordination
   - Maintained backward compatibility with existing HTML files
7. **Updated `templates/dashboard.html`** to reference all new module files in correct order

#### Benefits Achieved

- **Reduced dashboard.js size**: Main dashboard.js file is significantly smaller and focused only on initialization
- **Better organization**: Specific functionality is now organized into dedicated modules with clear separation of concerns
- **Improved maintainability**: Each component is in its own file, making it easier to update and debug
- **Enhanced reusability**: Modules can be more easily reused across different pages
- **Maintained compatibility**: All existing functionality preserved with backward compatibility
- **Component-based architecture**: Enables better code organization and future scalability

#### Files Created/Modified

1. `static/js/dashboard/charts/chart-manager.js` - Chart management
2. `static/js/dashboard/charts/*-chart.js` - Individual chart classes
3. `static/js/dashboard/data/api-client.js` - API client
4. `static/js/dashboard/data/data-loader.js` - Data loading operations
5. `static/js/dashboard/ui/table-renderer.js` - Table rendering
6. `static/js/dashboard/ui/section-manager.js` - Section navigation
7. `static/js/dashboard/ui/card-updater.js` - Card updating
8. `static/js/dashboard/utils/formatters.js` - Utility functions
9. `static/js/dashboard/utils/helpers.js` - Helper functions
10. `static/js/dashboard/dashboard.js` - Simplified entry point
11. `templates/dashboard.html` - Updated to reference new modules
12. Backup of original dashboard.js was created as `static/js/dashboard.js.backup`

#### Verification
All functionality remains intact after modularization. The dashboard works exactly as before but with a much cleaner, more maintainable code structure following the component-based architecture principles.

---

### Completed: Mobile_app.js Modularization

#### Overview
Successfully completed the modularization of the main `mobile_app.js` file as outlined in the sw.md document.

#### Tasks Completed

1. **Created directory structure**: `static/js/mobile_app/` with subdirectories for pwa, data, ui, charts, and utils
2. **Created PWA modules**:
   - `static/js/mobile_app/pwa/pwa-manager.js` - Handles PWA initialization (service worker, install prompts, notifications)
   - `static/js/mobile_app/pwa/notification-handler.js` - Handles push notifications and toast messages
3. **Created data modules**:
   - `static/js/mobile_app/data/api-client.js` - Handles API calls to backend endpoints
   - `static/js/mobile_app/data/data-loader.js` - Manages data loading operations
   - `static/js/mobile_app/data/offline-storage.js` - Handles caching and offline data storage
4. **Created UI modules**:
   - `static/js/mobile_app/ui/dashboard-updater.js` - Updates dashboard UI elements
   - `static/js/mobile_app/ui/payment-renderer.js` - Renders payment information
   - `static/js/mobile_app/ui/notification-renderer.js` - Renders notification history
   - `static/js/mobile_app/ui/navigation-manager.js` - Handles section and tab navigation
5. **Created chart modules**:
   - `static/js/mobile_app/charts/monitoring-chart.js` - Manages monitoring charts
6. **Created utility modules**:
   - `static/js/mobile_app/utils/formatters.js` - Contains formatting functions
   - `static/js/mobile_app/utils/helpers.js` - Contains helper functions
7. **Created main module**:
   - `static/js/mobile_app/main-module.js` - Main entry point that imports and coordinates all modules
8. **Updated HTML file**: `templates/mobile_app.html` to reference all new module files using ES6 modules
9. **Created backup**: Original mobile_app.js was backed up as `static/js/mobile_app.js.backup`

#### Benefits Achieved

- **Reduced mobile_app.js size**: Functionality distributed across focused, dedicated modules
- **Better organization**: Each module has a specific responsibility following separation of concerns
- **Improved maintainability**: Each component is in its own file, making it easier to update and debug
- **Enhanced reusability**: Modules can be more easily reused across different parts of the application
- **Maintained compatibility**: All existing functionality preserved with backward compatibility
- **Component-based architecture**: Enables better code organization and future scalability
- **Proper module handling**: Uses ES6 imports/exports for clean dependency management

#### Files Created/Modified

1. `static/js/mobile_app/pwa/pwa-manager.js` - PWA functionality
2. `static/js/mobile_app/pwa/notification-handler.js` - Notification handling
3. `static/js/mobile_app/data/api-client.js` - API client
4. `static/js/mobile_app/data/data-loader.js` - Data loading operations
5. `static/js/mobile_app/data/offline-storage.js` - Offline storage/caching
6. `static/js/mobile_app/ui/dashboard-updater.js` - Dashboard UI updates
7. `static/js/mobile_app/ui/payment-renderer.js` - Payment UI rendering
8. `static/js/mobile_app/ui/notification-renderer.js` - Notification UI rendering
9. `static/js/mobile_app/ui/navigation-manager.js` - Navigation management
10. `static/js/mobile_app/charts/monitoring-chart.js` - Chart management
11. `static/js/mobile_app/utils/formatters.js` - Formatting utilities
12. `static/js/mobile_app/utils/helpers.js` - Helper utilities
13. `static/js/mobile_app/main-module.js` - Main module entry point
14. `templates/mobile_app.html` - Updated to reference new modularized files
15. `static/js/mobile_app.js.backup` - Backup of original monolithic file

#### Verification
All functionality remains intact after modularization. The mobile app works exactly as before but with a much cleaner, more maintainable code structure following the component-based architecture principles. The modular approach allows for better code organization and future enhancements.

---

### Completed: Notification Dashboard.js Modularization

#### Overview
Successfully completed the modularization of the main `notification_dashboard.js` file as outlined in the sw.md document.

#### Tasks Completed

1. **Created directory structure**: `static/js/notification_dashboard/` with subdirectories for data, ui, forms, and utils
2. **Created data modules**:
   - `static/js/notification_dashboard/data/api-client.js` - Handles all API calls to notification endpoints
   - `static/js/notification_dashboard/data/data-loader.js` - Manages data loading operations for different dashboard sections
3. **Created UI modules**:
   - `static/js/notification_dashboard/ui/tab-manager.js` - Handles tab switching logic
   - `static/js/notification_dashboard/ui/overview-renderer.js` - Updates statistics cards and overview data
   - `static/js/notification_dashboard/ui/channel-renderer.js` - Renders channel list and status
   - `static/js/notification_dashboard/ui/template-renderer.js` - Renders notification templates
   - `static/js/notification_dashboard/ui/history-renderer.js` - Renders notification history
4. **Created form modules**:
   - `static/js/notification_dashboard/forms/notification-sender.js` - Handles quick notification form
   - `static/js/notification_dashboard/forms/settings-manager.js` - Handles settings form
   - `static/js/notification_dashboard/forms/template-creator.js` - Handles template creation form
5. **Created utility modules**:
   - `static/js/notification_dashboard/utils/formatters.js` - Contains formatting functions (icon mapping, date formatting)
   - `static/js/notification_dashboard/utils/toast-manager.js` - Handles toast notifications
6. **Simplified main `notification_dashboard.js`**:
   - Reduces the main file to an entry point that orchestrates all modules
   - Maintains backward compatibility with existing HTML onclick attributes
7. **Updated `templates/notification_dashboard.html`** to load all new module files in correct order

#### Benefits Achieved

- **Reduced coupling**: Each module has a specific responsibility following separation of concerns
- **Better organization**: Code is organized into logical layers (data, UI, forms, utilities)
- **Improved maintainability**: Each component is in its own file, making it easier to update and debug
- **Enhanced reusability**: Modules can be more easily reused across different parts of the application
- **Maintained compatibility**: All existing functionality preserved with backward compatibility
- **Component-based architecture**: Enables better code organization and future scalability
- **Proper module handling**: Uses ES6 imports/exports for clean dependency management

#### Files Created/Modified

1. `static/js/notification_dashboard/data/api-client.js` - API client for notification endpoints
2. `static/js/notification_dashboard/data/data-loader.js` - Data loading operations
3. `static/js/notification_dashboard/ui/tab-manager.js` - Tab switching logic
4. `static/js/notification_dashboard/ui/overview-renderer.js` - Overview rendering
5. `static/js/notification_dashboard/ui/channel-renderer.js` - Channel rendering
6. `static/js/notification_dashboard/ui/template-renderer.js` - Template rendering
7. `static/js/notification_dashboard/ui/history-renderer.js` - History rendering
8. `static/js/notification_dashboard/forms/notification-sender.js` - Notification sending
9. `static/js/notification_dashboard/forms/settings-manager.js` - Settings management
10. `static/js/notification_dashboard/forms/template-creator.js` - Template creation
11. `static/js/notification_dashboard/utils/formatters.js` - Formatting utilities
12. `static/js/notification_dashboard/utils/toast-manager.js` - Toast notifications
13. `static/js/notification_dashboard/notification_dashboard.js` - Simplified entry point
14. `templates/notification_dashboard.html` - Updated to reference new modules
15. `static/js/notification_dashboard.js.backup` - Backup of original monolithic file

#### Verification
All functionality remains intact after modularization. The notification dashboard works exactly as before but with a much cleaner, more maintainable code structure following the component-based architecture principles. The modular approach allows for better code organization and future enhancements.

---

### Completed: JavaScript File Organization and Cleanup

#### Overview
Successfully completed the organization and cleanup of JavaScript files in the static/js directory for better maintainability and structure.

#### Tasks Completed

1. **Identified unused JavaScript files**: Found 7 JavaScript files that were not referenced in any HTML templates
   - `ai-analyzer.js`
   - `analytics.js`
   - `audio-recorder.js`
   - `diagnosis-controller.js`
   - `diagnosis-ui.js`
   - `enhanced-registration.js`
   - `notification-manager.js`

2. **Created archived directory**: Created `static/js/archived/` directory to store unused files for backup

3. **Moved unused files to archived directory**: All 7 unused files were moved to the archived directory for potential future reference

4. **Identified used JavaScript files and their locations**:
   - `ai-diagnosis-demo.js` used in `ai_demo.html` and related to landing page functionality
   - `customer-dashboard.js` used in `base.html` and `base.htmly` and related to customer dashboard functionality
   - `sw.js` used in `mobile_app.html` for service worker functionality

5. **Created appropriate directories**:
   - `static/js/landing/` for landing page related JavaScript
   - `static/js/customer/` for customer-related JavaScript
   - `static/js/mobile_app/` for mobile application related JavaScript

6. **Moved used files to appropriate directories**:
   - `ai-diagnosis-demo.js` moved to `static/js/landing/`
   - `customer-dashboard.js` moved to `static/js/customer/`
   - `sw.js` moved to `static/js/mobile_app/`

7. **Updated HTML templates to reference new file paths**:
   - Updated `ai_demo.html` to use `/static/js/landing/ai-diagnosis-demo.js`
   - Updated `base.html` to use `/static/js/customer/customer-dashboard.js`
   - Updated `base.htmly` to use `/static/js/customer/customer-dashboard.js`
   - Updated `mobile_app.html` to use `/static/js/mobile_app/sw.js`

#### Benefits Achieved

- **Improved organization**: JavaScript files are now organized by functionality in appropriate directories
- **Reduced clutter**: Unused files have been archived, reducing directory clutter and confusion
- **Enhanced maintainability**: Related files are grouped together, making it easier to understand and update functionality
- **Better structure**: The project now has a more logical and consistent file structure
- **Backward compatibility**: All HTML templates were updated to maintain functionality after file reorganization
- **Future reference**: Archived files are preserved in case they are needed for future development

#### Files Created/Modified

1. `static/js/archived/` - Directory created to store archived JavaScript files
2. `static/js/landing/` - Directory created for landing page JavaScript files
3. `static/js/customer/` - Directory created for customer dashboard JavaScript files
4. Updated HTML templates:
   - `templates/ai_demo.html` - Updated script reference for ai-diagnosis-demo.js
   - `templates/base.html` - Updated script reference for customer-dashboard.js
   - `templates/base.htmly` - Updated script reference for customer-dashboard.js
   - `templates/mobile_app.html` - Updated script reference for sw.js
5. Moved JavaScript files:
   - `ai-analyzer.js` → `static/js/archived/`
   - `analytics.js` → `static/js/archived/`
   - `audio-recorder.js` → `static/js/archived/`
   - `diagnosis-controller.js` → `static/js/archived/`
   - `diagnosis-ui.js` → `static/js/archived/`
   - `enhanced-registration.js` → `static/js/archived/`
   - `notification-manager.js` → `static/js/archived/`
   - `ai-diagnosis-demo.js` → `static/js/landing/`
   - `customer-dashboard.js` → `static/js/customer/`
   - `sw.js` → `static/js/mobile_app/`

#### Verification
All functionality remains intact after reorganization. All HTML templates correctly reference the new file paths, and the application works exactly as before but with a much cleaner, more maintainable code structure. The modular approach allows for better code organization and future enhancements.

---

### Completed: Static HTML and Flask Template Organization

#### Overview
Successfully completed the organization of HTML files by properly categorizing static HTML files from Flask templates as outlined in the suggestion.md document.

#### Tasks Completed

1. **Analyzed HTML Files**: Distinguished between static HTML files in the `static/` directory and Flask templates in the `templates/` directory

2. **Created Directory Structure**: Implemented the proper directory structure with `static/pages/` and subdirectories:
   - `static/pages/` - Root for static HTML pages
   - `static/pages/labeling/` - For labeling-related pages
   - `static/pages/testing/` - For testing-related pages
   - `static/pages/storage/` - For storage-related pages

3. **Moved Static HTML Files**: Relocated static HTML files to appropriate directories:
   - `static/index.html` → `static/pages/index.html`
   - `static/showcase.html` → `static/pages/showcase.html`
   - `static/human_labeling_interface.html` → `static/pages/labeling/interface.html`
   - `static/labeling_management_dashboard.html` → `static/pages/labeling/management.html`
   - `static/noise_cancellation_test.html` → `static/pages/testing/noise_cancellation.html`
   - `static/smart_storage_dashboard.html` → `static/pages/storage/dashboard.html`
   - `static/audio_recorder_client.html` → `static/pages/audio_recorder_client.html`

4. **Updated Server Routing**: Modified `server/app.js` to handle the new file locations:
   - Updated root route (`/`) to serve `static/pages/showcase.html`
   - Added specific routes for each static page:
     - `/index` → `static/pages/index.html`
     - `/showcase` → `static/pages/showcase.html`
     - `/audio_recorder_client` → `static/pages/audio_recorder_client.html`
     - `/labeling/interface` → `static/pages/labeling/interface.html`
     - `/labeling/management` → `static/pages/labeling/management.html`
     - `/testing/noise_cancellation` → `static/pages/testing/noise_cancellation.html`
     - `/storage/dashboard` → `static/pages/storage/dashboard.html`

5. **Updated Internal Links**: Modified internal links in HTML files to reference the new routes and locations

6. **Verification**: Confirmed that all pages are functioning correctly after reorganization

#### Benefits Achieved

- **Improved Organization**: Static HTML files are now properly separated from Flask templates
- **Better Maintainability**: Clearer project structure with distinct purposes for each directory
- **Enhanced Scalability**: New static pages can be easily added in the appropriate subdirectories
- **Maintained Compatibility**: All existing functionality preserved with backward compatibility
- **Clearer Routing**: Specific routes for each static page make navigation more intuitive

#### Files Created/Modified

1. `static/pages/` directory and subdirectories - New directory structure
2. All previously static HTML files - Moved to appropriate locations
3. `server/app.js` - Updated routing to handle new file locations

#### Verification
All functionality remains intact after reorganization. The server correctly serves the showcase page at the root URL and other static pages at their designated routes. The project now has a cleaner, more maintainable structure with static HTML files properly separated from Flask templates.

---

### 2025-10-13: Header Layout Optimization

- **Objective:** Optimize the header layout to properly position elements with a large logo while maintaining visual alignment.
- **Changes:**
    - **Removed Header Border:** Eliminated the dividing line under the header to create a cleaner appearance
    - **Logo Positioning:** Positioned the logo at 180px size on the left side of the header
    - **Vertical Alignment:** Adjusted logo position with 10px top margin to align with the "무료체험하기" button
    - **Navigation Positioning:** Moved navigation elements (login, free trial button) to the right side of the header
    - **Header Height Adjustment:** Increased header height to 200px to properly accommodate the large logo
    - **Maintained Responsiveness:** Ensured layout remains responsive across different screen sizes
- **Benefits:**
    - **Visual Alignment:** Logo is now properly aligned with the primary CTA button
    - **Cleaner Design:** Removal of the dividing line creates a more modern, minimalist appearance
    - **Better Hierarchy:** Large logo creates a strong visual anchor while maintaining balanced layout
    - **Improved UX:** Clear separation of branding on the left and action items on the right
