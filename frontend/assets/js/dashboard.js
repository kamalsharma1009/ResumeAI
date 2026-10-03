/**
 * Dashboard Analytics and Visualization Controller
 * Deeply customized for Candidate (USER), Recruiter (HR), and Administrator (ADMIN).
 */

let atsChart = null;
let matchChart = null;
let skillChart = null;
let roleChart = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadDashboardData();
});

async function loadDashboardData() {
  try {
    const user = getUser();
    const role = (user && user.role) ? user.role.toUpperCase() : 'USER';
    const data = await apiCall('/analytics/dashboard');

    renderRoleDashboardLayout(role, user, data);
    renderKpis(role, data.kpi, data.user_metrics);
    renderCharts(data.charts, role);
    renderRecentScans(data.recent_scans, role);
  } catch (err) {
    showToast('Failed to load dashboard data: ' + err.message, 'error');
  }
}

/**
 * Customizes page headers, topbar buttons, and launchpad according to role
 */
function renderRoleDashboardLayout(role, user, data) {
  const titleArea = document.getElementById('dashboard-title-area');
  const topbarActions = document.getElementById('dashboard-topbar-actions');
  const launchpadContainer = document.getElementById('candidate-launchpad-container');
  const scansTitle = document.getElementById('scans-table-title');
  const scansBtn = document.getElementById('scans-table-btn');
  const headerRow = document.getElementById('scans-table-header-row');

  const fullName = (user && user.full_name) ? user.full_name : 'Candidate';

  if (role === 'USER') {
    // 1. CANDIDATE PORTAL VIEW
    if (titleArea) {
      titleArea.innerHTML = `
        <h2>Candidate Career Intelligence Portal 🚀</h2>
        <p>Welcome back, <strong style="color: var(--text-primary);">${fullName}</strong>! Track your ATS readiness, target role fit, and next milestones.</p>
      `;
    }

    if (topbarActions) {
      // Keep existing role switcher if present, replace action buttons
      const existingSwitcher = document.getElementById('role-switcher-wrapper');
      topbarActions.innerHTML = '';
      if (existingSwitcher) topbarActions.appendChild(existingSwitcher);

      const actionGroup = document.createElement('div');
      actionGroup.style.display = 'flex';
      actionGroup.style.gap = '10px';
      actionGroup.innerHTML = `
        <a href="/upload.html" class="btn btn-primary btn-sm">
          <span>📤 Upload / Update CV</span>
        </a>
        <a href="/report.html" class="btn btn-outline btn-sm">
          <span>📄 My Executive Report</span>
        </a>
      `;
      topbarActions.appendChild(actionGroup);
    }

    // Render Candidate Career Acceleration Launchpad
    if (launchpadContainer) {
      launchpadContainer.innerHTML = `
        <div class="candidate-launchpad">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <div>
              <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-primary);">⚡ Candidate Career Acceleration Hub</h3>
              <p style="font-size: 0.84rem; color: var(--text-muted); margin-top: 2px;">One-click tools to evaluate your resume, practice interviews, and bridge skill gaps</p>
            </div>
            <span class="badge badge-primary">Candidate Suite</span>
          </div>

          <div class="launchpad-grid">
            <div class="launchpad-card">
              <div>
                <div class="launchpad-icon cyan">⚡</div>
                <div class="launchpad-title">Instant Live Demo Scan</div>
                <div class="launchpad-desc">Test real-time AI extraction & ATS scoring with pre-calibrated engineer profiles:</div>
              </div>
              <div style="display: flex; flex-direction: column; gap: 6px; margin-top: 8px;">
                <button type="button" class="btn btn-sm btn-outline" onclick="quickDemoScan('Python')" style="text-align: left; justify-content: flex-start; font-size: 0.8rem;">
                  <span>🐍 Senior Python Backend</span>
                </button>
                <button type="button" class="btn btn-sm btn-outline" onclick="quickDemoScan('Priya')" style="text-align: left; justify-content: flex-start; font-size: 0.8rem;">
                  <span>🤖 Data Scientist & NLP</span>
                </button>
                <button type="button" class="btn btn-sm btn-outline" onclick="quickDemoScan('Alex')" style="text-align: left; justify-content: flex-start; font-size: 0.8rem;">
                  <span>☁️ DevOps Cloud Architect</span>
                </button>
              </div>
            </div>

            <div class="launchpad-card">
              <div>
                <div class="launchpad-icon blue">🗺️</div>
                <div class="launchpad-title">5-Phase Skill Roadmap</div>
                <div class="launchpad-desc">Personalized, step-by-step learning path tailored to close detected skill gaps and achieve senior engineering competence.</div>
              </div>
              <a href="/roadmap.html" class="btn btn-sm btn-secondary" style="width: 100%;">Explore My Roadmap →</a>
            </div>

            <div class="launchpad-card">
              <div>
                <div class="launchpad-icon emerald">💬</div>
                <div class="launchpad-title">AI Mock Interview Room</div>
                <div class="launchpad-desc">Prepare with tailored technical, system architecture, and behavioral questions calibrated to your resume.</div>
              </div>
              <a href="/interview.html" class="btn btn-sm btn-secondary" style="width: 100%;">Practice Interview Q&A →</a>
            </div>

            <div class="launchpad-card">
              <div>
                <div class="launchpad-icon amber">💼</div>
                <div class="launchpad-title">Matched Opportunities</div>
                <div class="launchpad-desc">Discover active job requisitions matching your current verified skills, and evaluate semantic fit in 1-click.</div>
              </div>
              <a href="/jobs.html" class="btn btn-sm btn-primary" style="width: 100%;">Check Job Matches →</a>
            </div>
          </div>
        </div>
      `;
    }

    if (scansTitle) scansTitle.textContent = 'My Resume Submissions & Calibration History';
    if (scansBtn) scansBtn.textContent = 'View My History';
    if (headerRow) {
      headerRow.innerHTML = `
        <th>Resume Version / File</th>
        <th>ATS Score</th>
        <th>Job Match</th>
        <th>Predicted Role</th>
        <th>Status</th>
        <th>Upload Date</th>
        <th>Actions</th>
      `;
    }

  } else if (role === 'HR') {
    // 2. RECRUITER DESK VIEW
    if (titleArea) {
      titleArea.innerHTML = `
        <h2>Recruiter Talent Acquisition Desk 📋</h2>
        <p>Candidate pipeline, ATS screening metrics, and talent requisition tracking</p>
      `;
    }

    if (topbarActions) {
      const existingSwitcher = document.getElementById('role-switcher-wrapper');
      topbarActions.innerHTML = '';
      if (existingSwitcher) topbarActions.appendChild(existingSwitcher);

      const actionGroup = document.createElement('div');
      actionGroup.style.display = 'flex';
      actionGroup.style.gap = '10px';
      actionGroup.innerHTML = `
        <a href="/jobs.html" class="btn btn-primary btn-sm">
          <span>💼 + Post New Job</span>
        </a>
        <a href="/upload.html" class="btn btn-secondary btn-sm">
          <span>📤 Screen Applicant CV</span>
        </a>
      `;
      topbarActions.appendChild(actionGroup);
    }

    if (launchpadContainer) launchpadContainer.innerHTML = '';
    if (scansTitle) scansTitle.textContent = 'Applicant Screening Queue & Candidate Pipeline';
    if (scansBtn) {
      scansBtn.textContent = 'Manage Talent Pool';
      scansBtn.href = '/candidate.html';
    }
    if (headerRow) {
      headerRow.innerHTML = `
        <th>Candidate / Applicant</th>
        <th>ATS Score</th>
        <th>Job Match</th>
        <th>Target Role</th>
        <th>Status</th>
        <th>Received Date</th>
        <th>Actions</th>
      `;
    }

  } else {
    // 3. ADMIN CONSOLE VIEW
    if (titleArea) {
      titleArea.innerHTML = `
        <h2>Platform Administration & System Governance 🛡️</h2>
        <p>Multi-tenant user registry, AI model calibration, audit logging and system health</p>
      `;
    }

    if (topbarActions) {
      const existingSwitcher = document.getElementById('role-switcher-wrapper');
      topbarActions.innerHTML = '';
      if (existingSwitcher) topbarActions.appendChild(existingSwitcher);

      const actionGroup = document.createElement('div');
      actionGroup.style.display = 'flex';
      actionGroup.style.gap = '10px';
      actionGroup.innerHTML = `
        <button type="button" onclick="triggerAdminReseed()" class="btn btn-primary btn-sm">
          <span>🔄 Re-Seed Demo Data</span>
        </button>
        <a href="/admin.html" class="btn btn-secondary btn-sm">
          <span>⚙️ Admin Console</span>
        </a>
      `;
      topbarActions.appendChild(actionGroup);
    }

    if (launchpadContainer) launchpadContainer.innerHTML = '';
    if (scansTitle) scansTitle.textContent = 'System-Wide Audit Trail & Model Evaluations';
    if (scansBtn) {
      scansBtn.textContent = 'Full System Audit';
      scansBtn.href = '/history.html';
    }
    if (headerRow) {
      headerRow.innerHTML = `
        <th>Target Entity / File</th>
        <th>ATS Metric</th>
        <th>Match Metric</th>
        <th>Role Classification</th>
        <th>Status</th>
        <th>Timestamp</th>
        <th>Actions</th>
      `;
    }
  }
}

/**
 * Renders the 6 KPI cards with role-specific meaning and numbers
 */
function renderKpis(role, kpi, userMetrics) {
  const statsGrid = document.getElementById('dashboard-stats-grid');
  if (!statsGrid) return;

  if (role === 'USER') {
    // CANDIDATE SPECIFIC METRICS
    const atsScore = userMetrics?.ats_score ?? (kpi?.avg_ats_score || 85.0);
    const topMatch = userMetrics?.top_job_match ?? (kpi?.avg_job_match || 90.0);
    const predictedRole = userMetrics?.predicted_role || 'Senior Python Backend Developer';
    const skillsCount = userMetrics?.skills_count || (kpi?.skills_detected || 16);
    const gapsCount = userMetrics?.skill_gaps_count || 3;
    const targetJob = userMetrics?.target_job || 'Senior Full Stack Engineer';
    const targetCompany = userMetrics?.target_company || 'FinTech Labs';

    statsGrid.innerHTML = `
      <div class="stat-card">
        <div class="stat-icon emerald">🎯</div>
        <div class="stat-content">
          <span class="stat-value">${atsScore}%</span>
          <span class="stat-label">My ATS Score</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon cyan">⚡</div>
        <div class="stat-content">
          <span class="stat-value">${topMatch}%</span>
          <span class="stat-label">Top Job Match Fit</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon blue">🧭</div>
        <div class="stat-content">
          <span class="stat-value" style="font-size: 1.15rem; line-height: 1.2; word-break: break-word;">${predictedRole}</span>
          <span class="stat-label">AI Predicted Role</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon rose">🧠</div>
        <div class="stat-content">
          <span class="stat-value">${skillsCount} Skills</span>
          <span class="stat-label">Verified in Resume</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon amber">🚀</div>
        <div class="stat-content">
          <span class="stat-value">${gapsCount} Skills</span>
          <span class="stat-label">Recommended to Gain</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon emerald">💬</div>
        <div class="stat-content">
          <span class="stat-value">Ready</span>
          <span class="stat-label">Interview Preparedness</span>
        </div>
      </div>
    `;

  } else if (role === 'HR') {
    // RECRUITER METRICS
    statsGrid.innerHTML = `
      <div class="stat-card">
        <div class="stat-icon blue">👥</div>
        <div class="stat-content">
          <span class="stat-value">${kpi?.total_resumes || 5}</span>
          <span class="stat-label">Active Talent Pool</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon cyan">⚡</div>
        <div class="stat-content">
          <span class="stat-value">${kpi?.resumes_analyzed || 5}</span>
          <span class="stat-label">Resumes Screened</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon emerald">🎯</div>
        <div class="stat-content">
          <span class="stat-value">${kpi?.avg_ats_score || 0}%</span>
          <span class="stat-label">Average Candidate ATS</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon amber">⚖️</div>
        <div class="stat-content">
          <span class="stat-value">${kpi?.avg_job_match || 0}%</span>
          <span class="stat-label">Average Job Match</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon rose">🧠</div>
        <div class="stat-content">
          <span class="stat-value">${kpi?.skills_detected || 0}</span>
          <span class="stat-label">Skills Cataloged</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon blue">💼</div>
        <div class="stat-content">
          <span class="stat-value">${kpi?.recommended_roles_count || 6}</span>
          <span class="stat-label">Active Job Openings</span>
        </div>
      </div>
    `;

  } else {
    // ADMIN METRICS
    statsGrid.innerHTML = `
      <div class="stat-card">
        <div class="stat-icon blue">👥</div>
        <div class="stat-content">
          <span class="stat-value">7</span>
          <span class="stat-label">Total System Users</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon cyan">📄</div>
        <div class="stat-content">
          <span class="stat-value">${kpi?.total_resumes || 5}</span>
          <span class="stat-label">Indexed Resumes</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon emerald">🎯</div>
        <div class="stat-content">
          <span class="stat-value">${kpi?.avg_ats_score || 0}%</span>
          <span class="stat-label">Platform ATS Mean</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon amber">💼</div>
        <div class="stat-content">
          <span class="stat-value">6</span>
          <span class="stat-label">Live Job Postings</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon rose">🕒</div>
        <div class="stat-content">
          <span class="stat-value">100+</span>
          <span class="stat-label">Audit Event Logs</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon emerald">🛡️</div>
        <div class="stat-content">
          <span class="stat-value">100%</span>
          <span class="stat-label">System Health</span>
        </div>
      </div>
    `;
  }
}

function renderCharts(charts, role) {
  if (!charts || typeof Chart === 'undefined') return;

  const chartTextColor = '#94a3b8';
  const chartGridColor = '#1e293b';

  // 1. ATS Score Distribution (Doughnut)
  const atsCtx = document.getElementById('atsDistChart')?.getContext('2d');
  if (atsCtx) {
    if (atsChart) atsChart.destroy();
    atsChart = new Chart(atsCtx, {
      type: 'doughnut',
      data: {
        labels: Object.keys(charts.ats_distribution || {}),
        datasets: [{
          data: Object.values(charts.ats_distribution || {}),
          backgroundColor: ['#f43f5e', '#f59e0b', '#3b82f6', '#10b981'],
          borderWidth: 2,
          borderColor: '#131d36'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: chartTextColor, boxWidth: 12 } }
        }
      }
    });
  }

  // 2. Job Match Distribution (Bar)
  const matchCtx = document.getElementById('matchDistChart')?.getContext('2d');
  if (matchCtx) {
    if (matchChart) matchChart.destroy();
    matchChart = new Chart(matchCtx, {
      type: 'bar',
      data: {
        labels: Object.keys(charts.job_match_distribution || {}),
        datasets: [{
          label: 'Matches',
          data: Object.values(charts.job_match_distribution || {}),
          backgroundColor: '#06b6d4',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: chartTextColor }, grid: { display: false } },
          y: { ticks: { color: chartTextColor, stepSize: 1 }, grid: { color: chartGridColor } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  // 3. Skills Frequency (Horizontal Bar)
  const skillCtx = document.getElementById('skillFreqChart')?.getContext('2d');
  if (skillCtx) {
    if (skillChart) skillChart.destroy();
    const skills = charts.skill_frequency || [];
    skillChart = new Chart(skillCtx, {
      type: 'bar',
      data: {
        labels: skills.map(s => s.skill),
        datasets: [{
          label: 'Market Demand',
          data: skills.map(s => s.count),
          backgroundColor: '#3b82f6',
          borderRadius: 6
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: chartTextColor, stepSize: 1 }, grid: { color: chartGridColor } },
          y: { ticks: { color: chartTextColor }, grid: { display: false } }
        },
        plugins: { legend: { display: false } }
      }
    });
  }

  // 4. Top Roles (Pie)
  const roleCtx = document.getElementById('topRolesChart')?.getContext('2d');
  if (roleCtx) {
    if (roleChart) roleChart.destroy();
    const roles = charts.top_roles || [];
    roleChart = new Chart(roleCtx, {
      type: 'pie',
      data: {
        labels: roles.map(r => r.role),
        datasets: [{
          data: roles.map(r => r.count),
          backgroundColor: ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'],
          borderWidth: 2,
          borderColor: '#131d36'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom', labels: { color: chartTextColor, boxWidth: 12 } }
        }
      }
    });
  }
}

function renderRecentScans(scans, role) {
  const tbody = document.getElementById('recent-scans-tbody');
  if (!tbody) return;

  if (!scans || scans.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 30px; color: var(--text-muted);">
      No resume scans recorded yet. <a href="/upload.html">Upload a resume</a> to begin!
    </td></tr>`;
    return;
  }

  tbody.innerHTML = scans.map(s => `
    <tr>
      <td>
        <div style="font-weight: 600; color: var(--text-primary);">${s.candidate_name || 'Candidate'}</div>
        <div style="font-size: 0.78rem; color: var(--text-muted);">${s.original_filename}</div>
      </td>
      <td>
        ${s.ats_score !== null ? `<span class="badge ${s.ats_score >= 70 ? 'badge-success' : 'badge-warning'}">${s.ats_score}%</span>` : '<span class="text-muted">-</span>'}
      </td>
      <td>
        ${s.job_match_score !== null ? `<span class="badge badge-cyan">${s.job_match_score}%</span>` : '<span class="text-muted">-</span>'}
      </td>
      <td>
        <span class="badge badge-primary">${s.top_role || 'Software Engineer'}</span>
      </td>
      <td>
        <span class="badge badge-success">${s.status}</span>
      </td>
      <td>${s.date}</td>
      <td>
        <div style="display: flex; gap: 8px;">
          <a href="/analysis.html?id=${s.resume_id}" class="btn btn-sm btn-secondary" title="View Full AI Analysis">View</a>
          <a href="${getAuthDownloadUrl('/api/reports/' + s.resume_id + '/download')}" target="_blank" class="btn btn-sm btn-outline" title="Download PDF Report">PDF</a>
        </div>
      </td>
    </tr>
  `).join('');
}

// Global Demo Scanner Trigger for Launchpad
window.quickDemoScan = async function(profileKey) {
  try {
    showToast(`Scanning demo ${profileKey} profile with NLP parser...`, 'info');
    const result = await apiCall(`/resumes/demo-scan?profile=${encodeURIComponent(profileKey)}`, 'POST');
    showToast('Demo scan complete! Opening AI analysis report...', 'success');
    setTimeout(() => {
      window.location.href = `/analysis.html?id=${result.resume_id}`;
    }, 600);
  } catch (err) {
    showToast('Failed to run demo scan: ' + err.message, 'error');
  }
};

// Global Admin Re-Seed Trigger
window.triggerAdminReseed = async function() {
  if (!confirm('Re-seed system demo data? This will reset all demo candidates, jobs, and evaluations.')) return;
  try {
    showToast('Re-seeding demo database...', 'info');
    const res = await apiCall('/analytics/reseed', 'POST');
    showToast(res.message || 'Database re-seeded successfully!', 'success');
    setTimeout(() => {
      window.location.reload();
    }, 800);
  } catch (err) {
    showToast('Re-seed failed: ' + err.message, 'error');
  }
};
