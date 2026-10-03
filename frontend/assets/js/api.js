/**
 * API and Authentication Client Utilities
 * Handles JWT bearer tokens, centralized fetch requests, and UI toasts.
 *
 * FIX: Separated 401 handling so that on login/register pages, the actual
 * backend error message is surfaced instead of the generic "Session expired".
 * Protected pages still redirect to /login.html?expired=1 on 401.
 */

const API_BASE = '/api';

// ================= AUTH UTILITIES =================
function getToken() {
  return localStorage.getItem('resumeai_token');
}

function setToken(token) {
  localStorage.setItem('resumeai_token', token);
}

function clearToken() {
  localStorage.removeItem('resumeai_token');
  localStorage.removeItem('resumeai_user');
}

function getUser() {
  const u = localStorage.getItem('resumeai_user');
  try {
    return u ? JSON.parse(u) : null;
  } catch (e) {
    return null;
  }
}

function setUser(user) {
  localStorage.setItem('resumeai_user', JSON.stringify(user));
}

function isLoggedIn() {
  const token = getToken();
  return !!(token && token.length > 10);
}

function logout() {
  clearToken();
  window.location.href = '/login.html';
}

// Detect if on a public (auth) page
function isPublicPage() {
  const path = window.location.pathname;
  const publicPages = ['/', '/index.html', '/login', '/login.html', '/register', '/register.html'];
  return publicPages.some(p => path === p || path.endsWith(p));
}

// ================= API CALL WRAPPER =================
async function apiCall(endpoint, method = 'GET', body = null, isFormData = false) {
  const headers = {};
  const token = getToken();

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const options = {
    method: method,
    headers: headers
  };

  if (body) {
    if (isFormData) {
      options.body = body;
    } else {
      headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify(body);
    }
  }

  let response;
  try {
    response = await fetch(`${API_BASE}${endpoint}`, options);
  } catch (networkErr) {
    console.error(`Network error on ${endpoint}:`, networkErr);
    throw new Error('Network error. Is the server running?');
  }

  // --- 401 Handling ---
  // On public pages (login/register/landing): DO NOT redirect, throw the real error
  // On protected pages: clear token and redirect to login with expired notice
  if (response.status === 401) {
    let errorDetail = 'Invalid credentials.';
    try {
      const errBody = await response.json();
      if (errBody && errBody.detail) {
        errorDetail = typeof errBody.detail === 'string' ? errBody.detail : JSON.stringify(errBody.detail);
      }
    } catch (_) { /* ignore json parse errors on error bodies */ }

    if (isPublicPage()) {
      // On login/register: just throw the real error, do NOT clear storage or redirect
      throw new Error(errorDetail);
    } else {
      // On protected pages: clear and redirect
      clearToken();
      window.location.href = '/login.html?expired=1';
      throw new Error('Session expired. Please log in again.');
    }
  }

  // Parse response body
  const contentType = response.headers.get('content-type');
  let data;
  if (contentType && contentType.includes('application/json')) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const errorMsg = (data && data.detail)
      ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))
      : `Request failed (${response.status})`;
    throw new Error(errorMsg);
  }

  return data;
}

// ================= TOAST NOTIFICATIONS =================
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;

  const icons = { success: '✅', error: '⚠️', warning: '⚠️', info: 'ℹ️' };
  const icon = icons[type] || 'ℹ️';

  toast.innerHTML = `<span>${icon}</span> <div>${message}</div>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// ================= UI HELPERS =================
function getScoreBadge(score) {
  if (score >= 80) return `<span class="badge badge-success">${score}% Excellent</span>`;
  if (score >= 65) return `<span class="badge badge-primary">${score}% Good</span>`;
  if (score >= 50) return `<span class="badge badge-warning">${score}% Moderate</span>`;
  return `<span class="badge badge-danger">${score}% Needs Work</span>`;
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function getAuthDownloadUrl(path) {
  const token = getToken();
  if (!token) return path;
  const separator = path.includes('?') ? '&' : '?';
  return `${path}${separator}token=${encodeURIComponent(token)}`;
}

function downloadReportPdf(resumeId) {
  const url = getAuthDownloadUrl(`/api/reports/${resumeId}/download`);
  window.open(url, '_blank');
}

// Setup common navigation and active state on DOM load
function initRoleBasedUI() {
  const currentPath = window.location.pathname;
  const onPublicPage = isPublicPage();

  // If already logged in and visiting login/register, go to appropriate dashboard
  if (onPublicPage && currentPath !== '/' && !currentPath.endsWith('/index.html') && isLoggedIn()) {
    const savedUser = getUser();
    if (savedUser && savedUser.role === 'ADMIN') {
      window.location.href = '/admin.html';
    } else {
      window.location.href = '/dashboard.html';
    }
    return;
  }

  // Protect internal routes — redirect to login if not authenticated
  if (!onPublicPage && !isLoggedIn()) {
    window.location.href = '/login.html';
    return;
  }

  const user = getUser();
  const role = (user && user.role) ? user.role.toUpperCase() : 'USER';

  // --- Role-Based Route Guards ---
  if (!onPublicPage) {
    if (currentPath.includes('admin') && role !== 'ADMIN') {
      showToast('Access denied: Admin privileges required.', 'warning');
      window.location.href = '/dashboard.html';
      return;
    }
    if (currentPath.includes('candidate') && role === 'USER') {
      showToast('Access denied: Candidate talent pool is for recruiters.', 'warning');
      window.location.href = '/dashboard.html';
      return;
    }
  }

  // Populate user profile info in sidebar footer if elements exist
  const userNameElem = document.getElementById('nav-user-name');
  const userRoleElem = document.getElementById('nav-user-role');
  const userAvatarElem = document.getElementById('nav-user-avatar');

  if (user) {
    if (userNameElem) userNameElem.textContent = user.full_name || 'User';
    if (userRoleElem) {
      let roleDisplay = 'CANDIDATE';
      userRoleElem.className = 'user-role-badge badge-user';
      if (role === 'HR') {
        roleDisplay = 'HR RECRUITER';
        userRoleElem.className = 'user-role-badge badge-hr';
      } else if (role === 'ADMIN') {
        roleDisplay = 'ADMINISTRATOR';
        userRoleElem.className = 'user-role-badge badge-admin';
      }
      userRoleElem.textContent = roleDisplay;
    }
    if (userAvatarElem) {
      const initials = (user.full_name || 'U').split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
      userAvatarElem.textContent = initials;
      if (role === 'USER') {
        userAvatarElem.style.borderColor = 'var(--accent-cyan)';
        userAvatarElem.style.color = 'var(--accent-cyan)';
        userAvatarElem.style.background = 'var(--accent-cyan-light)';
      } else if (role === 'HR') {
        userAvatarElem.style.borderColor = 'var(--accent-emerald)';
        userAvatarElem.style.color = 'var(--accent-emerald)';
        userAvatarElem.style.background = 'var(--accent-emerald-light)';
      } else {
        userAvatarElem.style.borderColor = '#818cf8';
        userAvatarElem.style.color = '#818cf8';
        userAvatarElem.style.background = 'rgba(99, 102, 241, 0.15)';
      }
    }
  }

  // Dynamically Render Role-Specific Sidebar Navigation
  renderRoleBasedSidebar(role, currentPath);

  // In-Page Global Role Switcher Pill in Topbar
  renderTopbarRoleSwitcher(role);

  // Dynamically adapt page titles, descriptions, and action buttons per role
  applyRoleBasedPageAdaptations(role, user, currentPath);

  // Bind logout buttons
  const logoutBtns = document.querySelectorAll('.btn-logout');
  logoutBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      logout();
    });
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initRoleBasedUI);
} else {
  initRoleBasedUI();
}


// ================= ROLE-BASED SIDEBAR =================
function renderRoleBasedSidebar(role, currentPath) {
  const sidebarMenu = document.querySelector('.sidebar-menu');
  if (!sidebarMenu) return;

  // Add distinct role badge under logo in sidebar header
  const sidebarHeader = document.querySelector('.sidebar-header');
  if (sidebarHeader) {
    let existingTag = document.getElementById('portal-role-tag');
    if (!existingTag) {
      existingTag = document.createElement('div');
      existingTag.id = 'portal-role-tag';
      sidebarHeader.appendChild(existingTag);
    }
    
    let tagText = '🎓 CANDIDATE PORTAL';
    let tagColor = 'var(--accent-cyan)';
    let tagBg = 'rgba(6, 182, 212, 0.15)';
    let tagBorder = 'rgba(6, 182, 212, 0.35)';

    if (role === 'HR') {
      tagText = '💼 RECRUITER SUITE';
      tagColor = 'var(--accent-emerald)';
      tagBg = 'rgba(16, 185, 129, 0.15)';
      tagBorder = 'rgba(16, 185, 129, 0.35)';
    } else if (role === 'ADMIN') {
      tagText = '⚙️ ADMIN CONSOLE';
      tagColor = '#818cf8';
      tagBg = 'rgba(99, 102, 241, 0.15)';
      tagBorder = 'rgba(99, 102, 241, 0.35)';
    }

    existingTag.style.cssText = `font-size: 0.70rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; color: ${tagColor}; background: ${tagBg}; border: 1px solid ${tagBorder}; padding: 3px 9px; border-radius: 9999px; margin-top: 6px; display: inline-block;`;
    existingTag.textContent = tagText;
  }

  let menuHtml = '';

  if (role === 'USER') {
    // CANDIDATE SPECIFIC SIDEBAR
    menuHtml = `
      <div class="menu-category">Candidate Hub</div>
      <a href="/dashboard.html" class="menu-item" data-path="dashboard">
        <i>📊</i> <span>My Dashboard</span>
      </a>
      <a href="/upload.html" class="menu-item" data-path="upload">
        <i>📤</i> <span>Upload & Calibrate CV</span>
      </a>
      <a href="/jobs.html" class="menu-item" data-path="jobs">
        <i>💼</i> <span>Job Matches & Fit</span>
      </a>

      <div class="menu-category">Career Intelligence</div>
      <a href="/recommendations.html" class="menu-item" data-path="recommendations">
        <i>🎯</i> <span>AI Career Insights</span>
      </a>
      <a href="/roadmap.html" class="menu-item" data-path="roadmap">
        <i>🗺️</i> <span>5-Phase Skill Roadmap</span>
      </a>
      <a href="/interview.html" class="menu-item" data-path="interview">
        <i>💬</i> <span>AI Mock Interview Prep</span>
      </a>

      <div class="menu-category">My Records & Reports</div>
      <a href="/analytics.html" class="menu-item" data-path="analytics">
        <i>📈</i> <span>Market Benchmarks</span>
      </a>
      <a href="/history.html" class="menu-item" data-path="history">
        <i>🕒</i> <span>My Scan History</span>
      </a>
      <a href="/report.html" class="menu-item" data-path="report">
        <i>📄</i> <span>My Executive Report</span>
      </a>
    `;
  } else if (role === 'HR') {
    // RECRUITER SPECIFIC SIDEBAR
    menuHtml = `
      <div class="menu-category">Recruiter Desk</div>
      <a href="/dashboard.html" class="menu-item" data-path="dashboard">
        <i>📊</i> <span>Talent Dashboard</span>
      </a>
      <a href="/jobs.html" class="menu-item" data-path="jobs">
        <i>💼</i> <span>Job Postings & Roles</span>
      </a>
      <a href="/candidate.html" class="menu-item" data-path="candidate">
        <i>👥</i> <span>Candidate Talent Pool</span>
      </a>
      <a href="/upload.html" class="menu-item" data-path="upload">
        <i>📤</i> <span>Screen Applicant CV</span>
      </a>

      <div class="menu-category">Hiring Intelligence</div>
      <a href="/analytics.html" class="menu-item" data-path="analytics">
        <i>📈</i> <span>Talent Analytics</span>
      </a>
      <a href="/history.html" class="menu-item" data-path="history">
        <i>🕒</i> <span>Applicant Audit Logs</span>
      </a>
      <a href="/report.html" class="menu-item" data-path="report">
        <i>📄</i> <span>Executive Dossiers</span>
      </a>
      <a href="/recommendations.html" class="menu-item" data-path="recommendations">
        <i>🎯</i> <span>Role Predictor Engine</span>
      </a>
    `;
  } else {
    // ADMIN CONSOLE SIDEBAR
    menuHtml = `
      <div class="menu-category">System & Governance</div>
      <a href="/admin.html" class="menu-item" data-path="admin">
        <i>⚙️</i> <span>Admin Console</span>
      </a>
      <a href="/dashboard.html" class="menu-item" data-path="dashboard">
        <i>📊</i> <span>Platform Overview</span>
      </a>
      <a href="/analytics.html" class="menu-item" data-path="analytics">
        <i>📈</i> <span>Platform Analytics</span>
      </a>
      <a href="/history.html" class="menu-item" data-path="history">
        <i>🕒</i> <span>Global Scan Audit</span>
      </a>

      <div class="menu-category">Talent & Jobs Oversight</div>
      <a href="/candidate.html" class="menu-item" data-path="candidate">
        <i>👥</i> <span>All Candidates</span>
      </a>
      <a href="/jobs.html" class="menu-item" data-path="jobs">
        <i>💼</i> <span>Job Postings</span>
      </a>
      <a href="/upload.html" class="menu-item" data-path="upload">
        <i>📤</i> <span>Resume Scanner</span>
      </a>
      <a href="/report.html" class="menu-item" data-path="report">
        <i>📄</i> <span>Executive Reports</span>
      </a>

      <div class="menu-category">Intelligence Engines</div>
      <a href="/recommendations.html" class="menu-item" data-path="recommendations">
        <i>🎯</i> <span>Career Predictor</span>
      </a>
      <a href="/roadmap.html" class="menu-item" data-path="roadmap">
        <i>🗺️</i> <span>Roadmap Generator</span>
      </a>
      <a href="/interview.html" class="menu-item" data-path="interview">
        <i>💬</i> <span>Interview Engine</span>
      </a>
    `;
  }

  sidebarMenu.innerHTML = menuHtml;

  // Highlight active link
  const menuLinks = sidebarMenu.querySelectorAll('.menu-item');
  menuLinks.forEach(link => {
    const dataPath = link.getAttribute('data-path');
    const href = link.getAttribute('href');
    if ((dataPath && currentPath.includes(dataPath)) || (href && currentPath.endsWith(href))) {
      link.classList.add('active');
    }
  });
}

// ================= TOPBAR QUICK ROLE SWITCHER =================
function renderTopbarRoleSwitcher(currentRole) {
  const topbar = document.querySelector('.app-topbar');
  if (!topbar || document.getElementById('role-switcher-wrapper')) return;

  const wrapper = document.createElement('div');
  wrapper.id = 'role-switcher-wrapper';
  wrapper.className = 'role-switcher-pill';

  wrapper.innerHTML = `
    <span class="role-switcher-label">View:</span>
    <button type="button" class="role-switcher-btn role-user ${currentRole === 'USER' ? 'active' : ''}" onclick="switchRoleDemo('USER')" title="Switch to Candidate View">
      <span>🎓 Candidate</span>
    </button>
    <button type="button" class="role-switcher-btn role-hr ${currentRole === 'HR' ? 'active' : ''}" onclick="switchRoleDemo('HR')" title="Switch to Recruiter View">
      <span>💼 Recruiter</span>
    </button>
    <button type="button" class="role-switcher-btn role-admin ${currentRole === 'ADMIN' ? 'active' : ''}" onclick="switchRoleDemo('ADMIN')" title="Switch to Admin View">
      <span>⚙️ Admin</span>
    </button>
  `;

  // Insert before topbar-actions or as first child of topbar-actions
  const topbarActions = topbar.querySelector('.topbar-actions');
  if (topbarActions) {
    topbarActions.insertBefore(wrapper, topbarActions.firstChild);
  } else {
    topbar.appendChild(wrapper);
  }
}

// Global Demo Role Switcher function
window.switchRoleDemo = async function(targetRole) {
  const target = targetRole.toUpperCase();
  let email = 'john.doe@gmail.com';
  let password = 'user123';

  if (target === 'HR') {
    email = 'hr@techcorp.com';
    password = 'hr123456';
  } else if (target === 'ADMIN') {
    email = 'admin@resumeai.com';
    password = 'admin123';
  }

  try {
    showToast(`Switching to ${target} view...`, 'info');
    const data = await apiCall('/auth/login', 'POST', { email, password });
    setToken(data.access_token);
    setUser(data.user);
    showToast(`Switched to ${target} portal! Updating view...`, 'success');

    setTimeout(() => {
      const path = window.location.pathname;
      if (target === 'USER' && (path.includes('admin') || path.includes('candidate'))) {
        window.location.href = '/dashboard.html';
      } else if (target === 'HR' && path.includes('admin')) {
        window.location.href = '/dashboard.html';
      } else {
        window.location.reload();
      }
    }, 400);
  } catch (err) {
    showToast('Failed to switch role: ' + err.message, 'error');
  }
};

// ================= DYNAMIC PAGE VIEW ADAPTATIONS =================
function applyRoleBasedPageAdaptations(role, user, currentPath) {
  const pageTitleArea = document.querySelector('.page-title-area');
  const h2 = pageTitleArea?.querySelector('h2');
  const p = pageTitleArea?.querySelector('p');

  // 1. JOBS PAGE
  if (currentPath.includes('jobs')) {
    const createBtn = document.getElementById('openCreateJobBtn');
    if (role === 'USER') {
      if (h2) h2.textContent = 'Explore Opportunities & Role Fit';
      if (p) p.textContent = 'Discover matched tech positions and check your CV compatibility in 1-click';
      if (createBtn) {
        // Replace create job button with upload / check match link
        createBtn.style.display = 'none';
        const topbarActions = document.querySelector('.topbar-actions');
        if (topbarActions && !document.getElementById('cand-match-action-btn')) {
          const checkBtn = document.createElement('a');
          checkBtn.id = 'cand-match-action-btn';
          checkBtn.href = '/upload.html';
          checkBtn.className = 'btn btn-primary btn-sm';
          checkBtn.innerHTML = '<span>📤 Upload / Update My CV</span>';
          topbarActions.appendChild(checkBtn);
        }
      }
    } else {
      if (h2) h2.textContent = 'Job Postings & Requisitions';
      if (p) p.textContent = 'Define role criteria, match candidates, and track applicants';
      if (createBtn) createBtn.style.display = '';
    }
  }

  // 2. UPLOAD PAGE
  if (currentPath.includes('upload')) {
    const cardTitle = document.querySelector('.card-header .card-title');
    if (role === 'USER') {
      if (h2) h2.textContent = 'Scan & Calibrate Your Resume';
      if (p) p.textContent = 'Extract skills, evaluate ATS readiness, and generate your personalized career roadmap';
      if (cardTitle) cardTitle.textContent = 'Upload Your Resume';
    } else {
      if (h2) h2.textContent = 'Applicant Resume Ingestion & AI Screening';
      if (p) p.textContent = 'Parse taxonomy, calculate ATS scores, and evaluate job fit for candidate applicants';
      if (cardTitle) cardTitle.textContent = 'Upload Candidate Resume';
    }
  }

  // 3. REPORT PAGE
  if (currentPath.includes('report')) {
    if (role === 'USER') {
      if (h2) h2.textContent = 'My Career Assessment & Executive Report';
      if (p) p.textContent = 'Official ATS score breakdown, skill gap diagnostics, and interview readiness dossier';
    } else {
      if (h2) h2.textContent = 'Executive Candidate Dossier & Reports';
      if (p) p.textContent = 'Official candidate assessment summaries ready for client & hiring manager dispatch';
    }
  }

  // 4. HISTORY PAGE
  if (currentPath.includes('history')) {
    if (role === 'USER') {
      if (h2) h2.textContent = 'My Evaluation & Scan History';
      if (p) p.textContent = 'Complete historical log of your uploaded resumes, ATS scores, and job fit calculations';
    } else {
      if (h2) h2.textContent = 'Applicant Screening Audit & Activity Log';
      if (p) p.textContent = 'System audit log of all candidate evaluations, scoring actions, and job matches';
    }
  }

  // 5. ANALYTICS PAGE
  if (currentPath.includes('analytics')) {
    if (role === 'USER') {
      if (h2) h2.textContent = 'Market Intelligence & Skill Benchmarks';
      if (p) p.textContent = 'Industry hiring trends, in-demand technical skills, and high-growth role benchmarks';
    } else {
      if (h2) h2.textContent = 'Talent Acquisition & Pipeline Analytics';
      if (p) p.textContent = 'Applicant scoring distributions, skill density metrics, and recruitment funnel insights';
    }
  }

  // 6. RECOMMENDATIONS PAGE
  if (currentPath.includes('recommendations')) {
    if (role === 'USER') {
      if (h2) h2.textContent = 'AI Career & Role Recommendations';
      if (p) p.textContent = 'Personalized career transition paths, target role fit, and high-impact skills to acquire';
    } else {
      if (h2) h2.textContent = 'Candidate Career & Role Classifier';
      if (p) p.textContent = 'Machine learning classification of candidate resumes and predicted job suitability';
    }
  }

  // 7. ROADMAP PAGE
  if (currentPath.includes('roadmap')) {
    if (role === 'USER') {
      if (h2) h2.textContent = 'My Personalized 5-Phase Skill Roadmap';
      if (p) p.textContent = 'Step-by-step career acceleration guide to bridge skill gaps and reach senior level';
    } else {
      if (h2) h2.textContent = 'Candidate Upskilling & Roadmap Generator';
      if (p) p.textContent = 'Structured learning tracks for candidate onboarding and technical gap remediation';
    }
  }

  // 8. INTERVIEW PAGE
  if (currentPath.includes('interview')) {
    if (role === 'USER') {
      if (h2) h2.textContent = 'AI Mock Interview Prep Room';
      if (p) p.textContent = 'Tailored technical and behavioral interview questions with model answers and evaluation tips';
    } else {
      if (h2) h2.textContent = 'Candidate Interview Question Generator';
      if (p) p.textContent = 'AI-generated technical and behavioral assessment questions tailored to candidate profiles';
    }
  }
}

