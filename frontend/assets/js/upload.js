/**
 * Resume Upload Controller with Multi-Stage AI Scanning Animation
 */

let selectedFile = null;

document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('resumeFileInput');
  const fileInfoBox = document.getElementById('selected-file-info');
  const fileNameDisplay = document.getElementById('selected-file-name');
  const fileSizeDisplay = document.getElementById('selected-file-size');
  const analyzeBtn = document.getElementById('startAnalyzeBtn');
  const scanProgressBox = document.getElementById('scan-progress-box');
  const progressBar = document.getElementById('scan-progress-bar');
  const progressText = document.getElementById('scan-progress-text');

  if (!dropzone || !fileInput) return;

  // Click dropzone to open native file picker
  dropzone.addEventListener('click', () => fileInput.click());

  // Drag and drop event listeners
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      handleFileSelected(files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });

  function handleFileSelected(file) {
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!['.pdf', '.docx'].includes(ext)) {
      showToast('Unsupported file type. Please select a .pdf or .docx file.', 'error');
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      showToast('File exceeds 15 MB size limit.', 'error');
      return;
    }

    selectedFile = file;
    fileNameDisplay.textContent = file.name;
    fileSizeDisplay.textContent = (file.size / 1024).toFixed(1) + ' KB';
    fileInfoBox.style.display = 'block';
    analyzeBtn.disabled = false;
  }

  // Handle Start Analysis
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', async () => {
      if (!selectedFile) {
        showToast('Please select a resume file first.', 'warning');
        return;
      }

      const targetRole = document.getElementById('targetRoleSelect')?.value || '';
      
      // Hide upload button and show scanning animation
      analyzeBtn.disabled = true;
      scanProgressBox.style.display = 'block';

      const scanSteps = [
        { pct: 15, text: 'Uploading document securely...', id: 'step-upload' },
        { pct: 35, text: 'Parsing text and contact credentials...', id: 'step-parse' },
        { pct: 55, text: 'Extracting technical and soft skills taxonomy...', id: 'step-skills' },
        { pct: 75, text: 'Evaluating experience and educational depth...', id: 'step-exp' },
        { pct: 90, text: 'Computing AI ATS-style compatibility score...', id: 'step-ats' },
        { pct: 98, text: 'Synthesizing recommendations & roadmaps...', id: 'step-recs' }
      ];

      // Simulate multi-stage visual progression while request processes
      let currentStepIdx = 0;
      const progressInterval = setInterval(() => {
        if (currentStepIdx < scanSteps.length) {
          const step = scanSteps[currentStepIdx];
          progressBar.style.width = step.pct + '%';
          progressText.textContent = step.text;
          
          const stepElem = document.getElementById(step.id);
          if (stepElem) {
            stepElem.classList.add('active');
            stepElem.querySelector('.step-status').textContent = 'Processing...';
          }
          currentStepIdx++;
        }
      }, 450);

      try {
        const formData = new FormData();
        formData.append('file', selectedFile);

        let endpoint = '/resumes/upload';
        if (targetRole) {
          endpoint += `?target_role=${encodeURIComponent(targetRole)}`;
        }

        const response = await apiCall(endpoint, 'POST', formData, true);
        
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressText.textContent = 'AI Scan Completed! Redirecting to report...';
        showToast('Resume analyzed successfully!', 'success');

        setTimeout(() => {
          window.location.href = `/analysis.html?id=${response.resume_id}`;
        }, 800);
      } catch (err) {
        clearInterval(progressInterval);
        showToast(err.message || 'Analysis failed. Please try again.', 'error');
        analyzeBtn.disabled = false;
        scanProgressBox.style.display = 'none';
      }
    });
  }

  // Handle Instant Demo Scan Buttons
  document.querySelectorAll('.demo-scan-btn').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      const profile = btn.getAttribute('data-profile') || 'Python';

      // Show scanning animation
      if (analyzeBtn) analyzeBtn.disabled = true;
      scanProgressBox.style.display = 'block';

      const scanSteps = [
        { pct: 20, text: 'Loading curated demonstration profile...', id: 'step-upload' },
        { pct: 40, text: 'Extracting candidate competencies & credentials...', id: 'step-parse' },
        { pct: 60, text: 'Mapping skills against industry taxonomy...', id: 'step-skills' },
        { pct: 80, text: 'Evaluating ATS score and career trajectory...', id: 'step-ats' },
        { pct: 95, text: 'Generating roadmap & interview prep...', id: 'step-recs' }
      ];

      let currentStepIdx = 0;
      const progressInterval = setInterval(() => {
        if (currentStepIdx < scanSteps.length) {
          const step = scanSteps[currentStepIdx];
          progressBar.style.width = step.pct + '%';
          progressText.textContent = step.text;
          const stepElem = document.getElementById(step.id);
          if (stepElem) {
            stepElem.classList.add('active');
            stepElem.querySelector('.step-status').textContent = 'Processing...';
          }
          currentStepIdx++;
        }
      }, 350);

      try {
        const response = await apiCall(`/resumes/demo-scan?profile=${encodeURIComponent(profile)}`, 'POST');
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        progressText.textContent = 'Demo Profile Analyzed! Opening Dashboard...';
        showToast(`Loaded ${response.candidate_name}'s profile!`, 'success');

        setTimeout(() => {
          window.location.href = `/analysis.html?id=${response.resume_id}`;
        }, 600);
      } catch (err) {
        clearInterval(progressInterval);
        showToast('Demo scan error: ' + err.message, 'error');
        if (analyzeBtn) analyzeBtn.disabled = false;
        scanProgressBox.style.display = 'none';
      }
    });
  });
});

