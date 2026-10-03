/**
 * Authentication Form Handlers (Login & Register)
 */

document.addEventListener('DOMContentLoaded', () => {
  // Check if expired notice requested
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('expired')) {
    showToast('Your session has expired. Please log in again.', 'warning');
    // Clean URL without reloading
    window.history.replaceState({}, document.title, '/login.html');
  }

  // 1. Login Form
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const submitBtn = loginForm.querySelector('button[type="submit"]');

      try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>Verifying...</span>';

        const data = await apiCall('/auth/login', 'POST', { email, password });
        setToken(data.access_token);
        setUser(data.user);
        showToast('Login successful! Redirecting...', 'success');

        setTimeout(() => {
          if (data.user.role === 'ADMIN') {
            window.location.href = '/admin.html';
          } else {
            window.location.href = '/dashboard.html';
          }
        }, 800);
      } catch (err) {
        showToast(err.message || 'Login failed. Please verify credentials.', 'error');
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Sign In';
      }
    });
  }

  // 2. Register Form
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fullName = document.getElementById('fullName').value.trim();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const confirmPassword = document.getElementById('confirmPassword')?.value;
      const roleElem = document.getElementById('role');
      const role = roleElem ? roleElem.value : 'USER';
      const submitBtn = registerForm.querySelector('button[type="submit"]');

      if (confirmPassword && password !== confirmPassword) {
        showToast('Passwords do not match.', 'error');
        return;
      }

      try {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>Creating Account...</span>';

        const data = await apiCall('/auth/register', 'POST', {
          full_name: fullName,
          email: email,
          password: password,
          role: role
        });

        setToken(data.access_token);
        setUser(data.user);
        showToast('Account registered successfully! Redirecting...', 'success');

        setTimeout(() => {
          window.location.href = '/dashboard.html';
        }, 800);
      } catch (err) {
        showToast(err.message || 'Registration failed.', 'error');
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Create Account';
      }
    });
  }

  // 3. Quick Demo Login Helpers
  window.fillDemoCredentials = function(role) {
    const emailField = document.getElementById('email');
    const pwdField = document.getElementById('password');
    if (!emailField || !pwdField) return;

    if (role === 'admin') {
      emailField.value = 'admin@resumeai.com';
      pwdField.value = 'admin123';
    } else if (role === 'hr') {
      emailField.value = 'hr@techcorp.com';
      pwdField.value = 'hr123456';
    } else if (role === 'user') {
      emailField.value = 'john.doe@gmail.com';
      pwdField.value = 'user123';
    }
    showToast(`Filled ${role.toUpperCase()} credentials. Click 'Sign In' to proceed!`, 'info');
  };
});
