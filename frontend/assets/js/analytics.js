/**
 * Analytics Page Dedicated Visualizations
 */

document.addEventListener('DOMContentLoaded', async () => {
  try {
    const data = await apiCall('/analytics/dashboard');
    renderAnalyticsPage(data);
  } catch (err) {
    showToast('Failed to load analytics: ' + err.message, 'error');
  }
});

function renderAnalyticsPage(data) {
  const chartTextColor = '#94a3b8';
  const chartGridColor = '#1e293b';

  // 1. Detailed ATS Distribution
  const atsCtx = document.getElementById('analyticsAtsChart')?.getContext('2d');
  if (atsCtx && data.charts.ats_distribution) {
    new Chart(atsCtx, {
      type: 'bar',
      data: {
        labels: Object.keys(data.charts.ats_distribution),
        datasets: [{
          label: 'Number of Resumes',
          data: Object.values(data.charts.ats_distribution),
          backgroundColor: ['#f43f5e', '#f59e0b', '#3b82f6', '#10b981'],
          borderRadius: 8
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

  // 2. Skill Frequency Full Chart
  const skillCtx = document.getElementById('analyticsSkillChart')?.getContext('2d');
  if (skillCtx && data.charts.skill_frequency) {
    new Chart(skillCtx, {
      type: 'polarArea',
      data: {
        labels: data.charts.skill_frequency.map(s => s.skill),
        datasets: [{
          data: data.charts.skill_frequency.map(s => s.count),
          backgroundColor: [
            'rgba(59, 130, 246, 0.7)',
            'rgba(6, 182, 212, 0.7)',
            'rgba(16, 185, 129, 0.7)',
            'rgba(245, 158, 11, 0.7)',
            'rgba(244, 63, 94, 0.7)',
            'rgba(139, 92, 246, 0.7)',
            'rgba(236, 72, 153, 0.7)',
            'rgba(20, 184, 166, 0.7)'
          ],
          borderWidth: 1,
          borderColor: '#131d36'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'right', labels: { color: chartTextColor, boxWidth: 12 } }
        }
      }
    });
  }

  // Populate Key Numbers
  document.getElementById('stat-total-resumes').textContent = data.kpi.total_resumes || 0;
  document.getElementById('stat-analyzed').textContent = data.kpi.resumes_analyzed || 0;
  document.getElementById('stat-avg-score').textContent = (data.kpi.avg_ats_score || 0) + '%';
  document.getElementById('stat-avg-match').textContent = (data.kpi.avg_job_match || 0) + '%';
}
