
  Logout Functionality on the Dashboard Page

  The logout functionality in the SignalCraft dashboard works as follows:

   1. UI Element: The logout link is defined in the sidebar component
      (static/dashboard-components/sidebar.html):

   1    <li class="nav-item"><a href="#" id="logout-link" class="nav-link"><i class="fas
     fa-sign-out-alt"></i> <span>로그아웃</span></a></li>

   2. Event Handler: In the dashboard template (templates/customer/dashboard.html), there's a click event
      handler for the logout link:

   1    document.getElementById('logout-link')?.addEventListener('click', function(e) {
   2        e.preventDefault();
   3        if (confirm('정말 로그아웃 하시겠습니까?')) {
   4            window.location.href = '/login';
   5        }
   6    });

   3. User Confirmation: When clicked, it first prompts the user with a confirmation dialog asking if they
      really want to log out.

   4. Redirection: If confirmed, it redirects the user to the /login page.

   5. Alternative Implementation: In other dashboard pages like anomalies-detail.html, a separate logoutUser()
      function handles the process:

   1    function logoutUser() {
   2        if (confirm('정말 로그아웃 하시겠습니까?')) {
   3            console.log('Logging out user...');
   4            window.location.href = '/login';
   5        }
   6    }

   6. Auth Manager: The AuthManager class in static/js/auth-manager.js contains a logout method that:
      - Clears user data from localStorage
      - Updates UI based on login status
      - Shows a notification
      - Reloads the page

  Authentication Flow Between Landing Page and Dashboard

  The authentication flow between the landing page and dashboard works as follows:

   1. Storage-Based: Authentication state is maintained via localStorage. The user's session is stored as
      'authToken' and 'currentUser' in localStorage.

   2. Initialization: When the AuthManager class is initialized, it checks localStorage for existing user data:

   1    init() {
   2        this.loadUserFromStorage();
   3        this.updateUI();
   4    }

   3. State Persistence: As long as the authentication token exists in localStorage, the user remains logged in
       across all pages, including when navigating from the landing page to the dashboard.

   4. UI Updates: The AuthManager automatically updates the UI based on the authentication state,
      hiding/showing login buttons and showing user information.

  I'll update the todo to reflect that I'm now moving to explain the authentication flow between the landing
   and dashboard pages.

 ╭─────────────────────────────────────────────────────────────────────────────╮
 │ ✓  TodoWrite Update todos                                                   │
 │                                                                             │
 │    ●  Analyze logout functionality on dashboard page                        │
 │    ◐  Explain how authentication flows between landing and dashboard pages  │
 ╰─────────────────────────────────────────────────────────────────────────────╯
✦ Authentication Flow Between Landing Page and Dashboard

  The authentication flow between the landing page and dashboard works as follows:

   1. Session Storage: When a user logs in (on the landing page or anywhere in the application), their
      authentication data is stored in localStorage using the AuthManager:

   1    saveUserToStorage(userData) {
   2        localStorage.setItem('currentUser', JSON.stringify(userData));
   3        this.currentUser = userData;
   4        this.isLoggedIn = true;
   5        this.updateUI();
   6    }

   2. Cross-Page Persistence: Since localStorage persists across browser sessions and different pages within
      the same domain, the authentication state is maintained when navigating from the landing page to the
      dashboard.

   3. Automatic State Check: Each page that includes the AuthManager automatically checks for existing
      authentication data when loaded through the init() method:

    1    loadUserFromStorage() {
    2        const userData = localStorage.getItem('currentUser');
    3        if (userData) {
    4            try {
    5                this.currentUser = JSON.parse(userData);
    6                this.isLoggedIn = true;
    7            } catch (e) {
    8                console.error('사용자 데이터 파싱 오류:', e);
    9                this.clearUserData();
   10            }
   11        }
   12    }

   4. UI Consistency: The AuthManager ensures that the UI is updated consistently across pages to reflect the
      current authentication status - showing logout buttons when logged in and login/register buttons when not
       logged in.

   5. Token Validation: The auth-manager.js in the auth directory also includes a verification method that can
      validate the stored token with the backend:

    1    async updateLoginStatus() {
    2        const token = localStorage.getItem('authToken');
    3        if (!token) {
    4            showLoggedOutUI();
    5            return;
    6        }
    7
    8        try {
    9            const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
   10                headers: {
   11                    'Authorization': `Bearer ${token}`
   12                }
   13            });
   14            // Update UI based on verification result
   15        } catch (error) {
   16            showLoggedOutUI();
   17        }
   18    }

  This approach ensures that once a user logs in on the landing page, they remain logged in when navigating
  to the dashboard and other protected pages, since the authentication state is preserved in localStorage
  and checked on each page load.
