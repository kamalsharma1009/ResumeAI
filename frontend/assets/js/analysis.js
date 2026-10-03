/**
 * Detailed Resume Analysis View Controller
 */

let currentResumeId = null;

document.addEventListener('DOMContentLoaded', async () => {
  const urlParams = new URLSearchParams(window.location.search);
  currentResumeId = urlParams.get('id');

  if (!currentResumeId) {
    // If no id, attempt to fetch the latest resume for user
    try {
      const resumes = await apiCall('/resumes');
      if (resumes && resumes.length > 0) {
        currentResumeId = resumes[0].id;
      } else {
        window.location.href = '/upload.html';
        return;
      }
    } catch (e) {
      window.location.href = '/upload.html';
      return;
    }
  }

  await loadAnalysis(currentResumeId);
  setupJobMatchModal();
});

async function loadAnalysis(resumeId) {
  try {
    const data = await apiCall(`/analysis/${resumeId}`);
    renderCandidateInfo(data.candidate);
    renderATSScore(data.ats_breakdown);
    renderSkills(data.skills_by_category);
    renderPredictedRoles(data.predicted_roles);
    renderRecommendations(data.recommendations);
    renderJobMatch(data.latest_job_match);
    renderSkillGaps(data.skill_gaps);

    // Update links
    const pdfBtn = document.getElementById('btn-download-pdf');
    if (pdfBtn) {
      pdfBtn.href = getAuthDownloadUrl(`/api/reports/${resumeId}/download`);
      pdfBtn.target = '_blank';
    }
    const roadmapBtn = document.getElementById('btn-view-roadmap');
    if (roadmapBtn) {
      roadmapBtn.href = `/roadmap.html?id=${resumeId}`;
    }
    const interviewBtn = document.getElementById('btn-view-interview');
    if (interviewBtn) {
      interviewBtn.href = `/interview.html?id=${resumeId}`;
    }
  } catch (err) {
    showToast('Failed to load analysis: ' + err.message, 'error');
  }
}

function renderCandidateInfo(cand) {
  if (!cand) return;
  document.getElementById('cand-name').textContent = cand.name || 'Candidate';
  document.getElementById('cand-email').textContent = cand.email || 'Not specified';
  document.getElementById('cand-phone').textContent = cand.phone || 'Not specified';
  document.getElementById('cand-exp').textContent = (cand.experience_years || 0) + ' Years';
  document.getElementById('cand-loc').textContent = cand.location || 'Not Specified';
  document.getElementById('cand-filename').textContent = cand.original_filename || '';
}

function renderATSScore(scores) {
  if (!scores) return;
  const overall = scores.overall_ats_score || 0;
  
  // Animate Circular Gauge
  const circle = document.getElementById('ats-gauge-circle');
  const numberElem = document.getElementById('ats-gauge-number');
  if (circle && numberElem) {
    const radius = 70;
    const circumference = 2 * Math.PI * radius;
    circle.style.strokeDasharray = `${circumference}`;
    
    // Determine color
    if (overall >= 75) {
      circle.style.stroke = '#10b981'; // Emerald
    } else if (overall >= 60) {
      circle.style.stroke = '#3b82f6'; // Blue
    } else {
      circle.style.stroke = '#f59e0b'; // Amber
    }

    const offset = circumference - (overall / 100) * circumference;
    setTimeout(() => {
      circle.style.strokeDashoffset = offset;
      numberElem.textContent = overall + '%';
    }, 200);
  }

  // Sub-scores
  setProgressBar('score-skills', scores.skills_score);
  setProgressBar('score-exp', scores.experience_score);
  setProgressBar('score-edu', scores.education_score);
  setProgressBar('score-kw', scores.keyword_score);
  setProgressBar('score-comp', scores.completeness_score);
  setProgressBar('score-fmt', scores.formatting_score);
}

function setProgressBar(elemId, val) {
  const bar = document.getElementById(elemId);
  const text = document.getElementById(elemId + '-val');
  if (bar) bar.style.width = (val || 0) + '%';
  if (text) text.textContent = (val || 0) + '%';
}

function renderSkills(skillsByCat) {
  const container = document.getElementById('skills-categorized-container');
  if (!container) return;

  const cats = Object.keys(skillsByCat || {});
  if (cats.length === 0) {
    container.innerHTML = '<p class="text-muted">No specific skill matches detected.</p>';
    return;
  }

  container.innerHTML = cats.map(cat => `
    <div style="margin-bottom: 16px;">
      <h5 style="font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; margin-bottom: 8px;">
        ${cat}
      </h5>
      <div style="display: flex; flex-wrap: wrap; gap: 8px;">
        ${skillsByCat[cat].map(s => `<span class="badge badge-primary">${s}</span>`).join('')}
      </div>
    </div>
  `).join('');
}

function renderPredictedRoles(roles) {
  const container = document.getElementById('predicted-roles-container');
  if (!container) return;

  if (!roles || roles.length === 0) {
    container.innerHTML = '<p class="text-muted">No roles predicted.</p>';
    return;
  }

  container.innerHTML = roles.map(r => `
    <div style="background-color: var(--bg-surface); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 16px; margin-bottom: 12px;">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
        <span style="font-weight: 700; color: var(--text-primary); font-size: 1rem;">${r.role_title}</span>
        <span class="badge ${r.confidence_score >= 70 ? 'badge-success' : 'badge-cyan'}">${r.confidence_score}% Fit</span>
      </div>
      <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 8px;">${r.description}</p>
      <div style="font-size: 0.8rem; color: var(--accent-cyan);">
        <strong>AI Insight:</strong> ${r.explanation}
      </div>
    </div>
  `).join('');
}

function renderRecommendations(recs) {
  const container = document.getElementById('recommendations-container');
  if (!container) return;

  if (!recs || recs.length === 0) {
    container.innerHTML = '<p class="text-muted">Resume meets foundational benchmarks with no critical alerts.</p>';
    return;
  }

  container.innerHTML = recs.map(rec => {
    let badgeClass = 'badge-primary';
    if (rec.priority === 'High') badgeClass = 'badge-danger';
    if (rec.priority === 'Medium') badgeClass = 'badge-warning';

    return `
      <div style="background-color: var(--bg-surface); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 16px; margin-bottom: 12px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
          <h5 style="font-size: 0.95rem; font-weight: 600; color: var(--text-primary);">${rec.title}</h5>
          <span class="badge ${badgeClass}">${rec.priority} Priority</span>
        </div>
        <p style="font-size: 0.86rem; color: var(--text-secondary);">${rec.description}</p>
      </div>
    `;
  }).join('');
}

function renderJobMatch(match) {
  const container = document.getElementById('job-match-section');
  if (!container) return;

  if (!match) {
    container.innerHTML = `
      <div style="text-align: center; padding: 24px; background-color: var(--bg-surface); border-radius: var(--radius-md); border: 1px dashed var(--border-light);">
        <p style="color: var(--text-secondary); margin-bottom: 14px;">No job description compared yet.</p>
        <button class="btn btn-sm btn-primary" onclick="openJobMatchModal()">Match Against a Job</button>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div style="background-color: var(--bg-surface); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 20px;">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px;">
        <div>
          <h4 style="font-size: 1.1rem; color: var(--text-primary);">${match.job_title}</h4>
          <span style="font-size: 0.85rem; color: var(--text-muted);">${match.company}</span>
        </div>
        <div style="text-align: right;">
          <span style="font-size: 1.8rem; font-weight: 700; color: var(--accent-cyan); font-family: var(--font-display);">${match.match_score}%</span>
          <div style="font-size: 0.75rem; color: var(--text-muted);">Match Compatibility</div>
        </div>
      </div>
      <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 14px;">${match.analysis_notes || ''}</p>
      
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">
        <div>
          <h6 style="font-size: 0.8rem; color: var(--accent-emerald); text-transform: uppercase; margin-bottom: 6px;">Matched Skills</h6>
          <div style="display: flex; flex-wrap: wrap; gap: 6px;">
            ${(match.matched_skills || []).map(s => `<span class="badge badge-success">${s}</span>`).join('') || '<span class="text-muted">None</span>'}
          </div>
        </div>
        <div>
          <h6 style="font-size: 0.8rem; color: var(--accent-rose); text-transform: uppercase; margin-bottom: 6px;">Missing Requirements</h6>
          <div style="display: flex; flex-wrap: wrap; gap: 6px;">
            ${(match.missing_skills || []).map(s => `<span class="badge badge-danger">${s}</span>`).join('') || '<span class="badge badge-success">All matched!</span>'}
          </div>
        </div>
      </div>
      <div style="margin-top: 16px;">
        <button class="btn btn-sm btn-outline" onclick="openJobMatchModal()">Compare with Another Job</button>
      </div>
    </div>
  `;
}

function renderSkillGaps(gaps) {
  const container = document.getElementById('skill-gaps-container');
  if (!container) return;

  if (!gaps || gaps.length === 0) {
    container.innerHTML = '<p class="text-muted">No critical skill gaps flagged.</p>';
    return;
  }

  container.innerHTML = gaps.map(g => `
    <div style="background-color: var(--bg-surface); border: 1px solid var(--border-light); border-radius: var(--radius-md); padding: 14px; margin-bottom: 10px;">
      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
        <span style="font-weight: 700; color: var(--text-primary); font-size: 0.95rem;">${g.missing_skill}</span>
        <span class="badge ${g.importance === 'Critical' ? 'badge-danger' : 'badge-warning'}">${g.importance}</span>
      </div>
      <p style="font-size: 0.84rem; color: var(--text-secondary); margin-bottom: 6px;">${g.reason}</p>
      <div style="font-size: 0.8rem; color: var(--primary);">
        <strong>Suggested Path:</strong> ${g.suggested_learning_path}
      </div>
    </div>
  `).join('');
}

// Modal handling for matching against job
async function setupJobMatchModal() {
  const modal = document.getElementById('jobMatchModal');
  const closeBtn = document.getElementById('closeMatchModalBtn');
  const runBtn = document.getElementById('runJobMatchBtn');
  const jobSelect = document.getElementById('modalJobSelect');

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => modal.classList.remove('show'));
  }

  window.openJobMatchModal = async function() {
    if (!modal || !jobSelect) return;
    try {
      const jobs = await apiCall('/jobs');
      jobSelect.innerHTML = jobs.map(j => `<option value="${j.id}">${j.title} (${j.company})</option>`).join('');
      modal.classList.add('show');
    } catch (e) {
      showToast('Failed to load jobs list: ' + e.message, 'error');
    }
  };

  if (runBtn && jobSelect) {
    runBtn.addEventListener('click', async () => {
      const jobId = jobSelect.value;
      if (!jobId || !currentResumeId) return;

      try {
        runBtn.disabled = true;
        runBtn.textContent = 'Comparing...';
        await apiCall(`/jobs/${jobId}/match/${currentResumeId}`, 'POST');
        showToast('Job match completed!', 'success');
        modal.classList.remove('show');
        await loadAnalysis(currentResumeId);
      } catch (err) {
        showToast('Match failed: ' + err.message, 'error');
      } finally {
        runBtn.disabled = false;
        runBtn.textContent = 'Run AI Matching';
      }
    });
  }
}
