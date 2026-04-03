const BASE_API_URL = "http://127.0.0.1:8000";
const AUTH_STORAGE_KEY = "cvsir_access_token";
const USER_STORAGE_KEY = "cvsir_user";

const JOB_ROLES = [
  "Data Analyst",
  "Data Engineer",
  "Business Analyst",
  "Machine Learning Engineer",
  "AI Engineer",
  "Backend Developer",
  "Frontend Developer",
  "Full Stack Developer",
  "DevOps Engineer",
  "Cloud Engineer",
  "Cyber Security Analyst",
  "UI/UX Designer",
  "Product Manager",
  "QA Engineer",
  "Mobile App Developer"
];

function getToken() {
  return localStorage.getItem(AUTH_STORAGE_KEY);
}

function setSession(token, user) {
  localStorage.setItem(AUTH_STORAGE_KEY, token);
  localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  updateAuthUI();
}

function clearSession() {
  localStorage.removeItem(AUTH_STORAGE_KEY);
  localStorage.removeItem(USER_STORAGE_KEY);
  updateAuthUI();
}

function getAuthHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function setAuthMessage(message, type = "") {
  const authMessage = document.getElementById("authMessage");
  authMessage.textContent = message;
  authMessage.className = `auth-message ${type}`.trim();
}

function updateAuthUI() {
  const token = getToken();
  const analyzerSection = document.getElementById("analyzerSection");
  const authStatus = document.getElementById("authStatus");
  const user = JSON.parse(localStorage.getItem(USER_STORAGE_KEY) || "null");

  if (token && user) {
    analyzerSection.style.display = "block";
    authStatus.textContent = `Logged in as ${user.name}`;
  } else {
    analyzerSection.style.display = "none";
    authStatus.textContent = "Not logged in";
  }
}

async function callApi(path, options = {}) {
  const mergedOptions = {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...getAuthHeaders()
    }
  };

  const response = await fetch(`${BASE_API_URL}${path}`, mergedOptions);
  const responseData = await response.json();

  if (!response.ok) {
    throw new Error(responseData.detail || responseData.error || "Request failed");
  }

  return responseData;
}

async function register(event) {
  event.preventDefault();

  try {
    const body = {
      name: document.getElementById("registerName").value.trim(),
      email: document.getElementById("registerEmail").value.trim(),
      password: document.getElementById("registerPassword").value
    };

    const data = await callApi("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    setSession(data.access_token, data.user);
    setAuthMessage("Registration successful. You can now analyze resumes.", "success");
    event.target.reset();

  } catch (error) {
    setAuthMessage(error.message, "error");
  }
}

async function login(event) {
  event.preventDefault();

  try {
    const body = {
      email: document.getElementById("loginEmail").value.trim(),
      password: document.getElementById("loginPassword").value
    };

    const data = await callApi("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    setSession(data.access_token, data.user);
    setAuthMessage("Login successful.", "success");
    event.target.reset();

  } catch (error) {
    setAuthMessage(error.message, "error");
  }
}

async function validateExistingToken() {
  if (!getToken()) {
    updateAuthUI();
    return;
  }

  try {
    const user = await callApi("/auth/me", { method: "GET" });
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
  } catch (_error) {
    clearSession();
  }

  updateAuthUI();
}

function goToStep(stepNumber) {
  document.querySelectorAll(".step-content").forEach(el => {
    el.classList.remove("active");
  });

  document.querySelectorAll(".step").forEach((el, index) => {
    el.classList.remove("active");
    if (index < stepNumber) {
      el.classList.add("active");
    }
  });

  document.getElementById(`step${stepNumber}`).classList.add("active");
}

const roleInput = document.getElementById("targetRole");
const suggestionsBox = document.getElementById("roleSuggestions");

if (roleInput) {
  roleInput.addEventListener("input", () => {
    const query = roleInput.value.toLowerCase().trim();
    suggestionsBox.innerHTML = "";

    if (!query) {
      suggestionsBox.style.display = "none";
      return;
    }

    const matches = JOB_ROLES.filter(role => role.toLowerCase().includes(query));

    if (matches.length === 0) {
      suggestionsBox.style.display = "none";
      return;
    }

    matches.forEach(role => {
      const div = document.createElement("div");
      div.className = "suggestion-item";
      div.textContent = role;

      div.onclick = () => {
        roleInput.value = role;
        suggestionsBox.style.display = "none";
      };

      suggestionsBox.appendChild(div);
    });

    suggestionsBox.style.display = "block";
  });
}

document.addEventListener("click", (event) => {
  if (suggestionsBox && !event.target.closest(".autocomplete-container")) {
    suggestionsBox.style.display = "none";
  }
});

async function analyze(event) {
  if (event) event.preventDefault();

  if (!getToken()) {
    setAuthMessage("Please login first.", "error");
    return;
  }

  const resumeFile = document.getElementById("resumeFile").files[0];
  const targetRole = document.getElementById("targetRole").value;
  const jdText = document.getElementById("jdText").value;
  const experienceYears = document.getElementById("experienceYears")?.value || 0;
  const projects = document.getElementById("projectsCount")?.value || 0;

  if (!resumeFile) {
    alert("Please upload your resume");
    return;
  }

  if (!targetRole) {
    alert("Please enter a job title");
    return;
  }

  const formData = new FormData();
  formData.append("resume", resumeFile);
  formData.append("target_role", targetRole);
  formData.append("experience_years", experienceYears);
  formData.append("projects", projects);

  if (jdText) {
    formData.append("job_description_text", jdText);
  }

  try {
    const data = await callApi("/analyze", {
      method: "POST",
      body: formData
    });

    renderResults(data);

  } catch (error) {
    setAuthMessage(error.message, "error");
  }
}

function renderResults(data) {
  document.getElementById("resTargetRole").textContent = data.target_role || "-";
  document.getElementById("resRoleMatch").textContent = `${data.role_match_percentage}%`;
  document.getElementById("resJdMatch").textContent =
    data.jd_match_percentage !== null ? `${data.jd_match_percentage}%` : "N/A";

  renderList("roleMissingSkillsList", data.role_missing_skills);
  renderList("roleExtraSkillsList", data.role_extra_skills);
  renderList("jdMissingSkillsList", data.jd_missing_skills);

  renderChart(data.role_matches || {});
  renderRecommendedJobs(data);
}

function renderList(id, items = []) {
  const ul = document.getElementById(id);
  if (!ul) return;

  ul.innerHTML = "";

  if (!items || items.length === 0) {
    ul.innerHTML = "<li>No items 🎉</li>";
    return;
  }

  items.forEach(skill => {
    const li = document.createElement("li");
    li.textContent = skill;
    ul.appendChild(li);
  });
}

let roleChart = null;

function renderChart(roleMatches) {
  const labels = Object.keys(roleMatches);
  const values = Object.values(roleMatches);

  const canvas = document.getElementById("roleChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  if (roleChart) roleChart.destroy();

  roleChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Role Match %",
        data: values,
        backgroundColor: "#2563eb",
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: { beginAtZero: true, max: 100 }
      }
    }
  });
}

async function renderRecommendedJobs(data) {
  const container = document.getElementById("recommendedJobs");
  container.innerHTML = "";

  const rankedRoles = Object.entries(data.career_profile || {})
    .sort((a, b) => b[1].score - a[1].score)
    .slice(0, 3);

  for (const [role, profile] of rankedRoles) {
    const formData = new FormData();
    formData.append("role", role);
    formData.append("level", profile.level);

    try {
      const result = await callApi("/job-recommendations", {
        method: "POST",
        body: formData
      });

      const card = document.createElement("div");
      card.className = "job-card";

      card.innerHTML = `
        <h4>${role}</h4>
        <div class="job-meta">
          <span><strong>Level:</strong> ${profile.level}</span>
          <span><strong>Readiness:</strong> ${profile.score}%</span>
        </div>
        <div class="job-links">
          <a class="job-btn linkedin" href="${result.external_links.linkedin}" target="_blank">LinkedIn Jobs →</a>
          <a class="job-btn indeed" href="${result.external_links.indeed}" target="_blank">Indeed Jobs →</a>
        </div>
      `;

      container.appendChild(card);

    } catch (error) {
      setAuthMessage(error.message, "error");
    }
  }
}

document.getElementById("registerForm")?.addEventListener("submit", register);
document.getElementById("loginForm")?.addEventListener("submit", login);
document.getElementById("logoutBtn")?.addEventListener("click", () => {
  clearSession();
  setAuthMessage("Logged out.", "success");
});

validateExistingToken();
