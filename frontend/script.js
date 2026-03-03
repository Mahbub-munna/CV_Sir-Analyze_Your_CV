// -----------------------------
// Job Roles (Frontend Copy)
// -----------------------------
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

// -----------------------------
// Stepper Logic
// -----------------------------
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

// -----------------------------
// Autocomplete Logic
// -----------------------------
const roleInput = document.getElementById("targetRole");
const suggestionsBox = document.getElementById("roleSuggestions");

roleInput.addEventListener("input", () => {
  const query = roleInput.value.toLowerCase().trim();
  suggestionsBox.innerHTML = "";

  if (!query) {
    suggestionsBox.style.display = "none";
    return;
  }

  const matches = JOB_ROLES.filter(role =>
    role.toLowerCase().includes(query)
  );

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

document.addEventListener("click", (e) => {
  if (!e.target.closest(".autocomplete-container")) {
    suggestionsBox.style.display = "none";
  }
});

// -----------------------------
// Analyze (API Call)
// -----------------------------
async function analyze(event) {
  if (event) {
    event.preventDefault();
    event.stopPropagation();
  }

  const resumeFile = document.getElementById("resumeFile").files[0];
  const jdText = document.getElementById("jdText").value;
  const targetRole = document.getElementById("targetRole").value;

  if (!resumeFile) {
    alert("Please upload your resume!");
    return;
  }

  if (!targetRole) {
    alert("Please enter a job title!");
    return;
  }

  // Loading UI
  document.getElementById("resTargetRole").textContent = targetRole;
  document.getElementById("resRoleMatch").textContent = "Analyzing...";
  document.getElementById("resJdMatch").textContent = jdText ? "Analyzing..." : "N/A";

  const formData = new FormData();
  formData.append("resume", resumeFile);
  formData.append("target_role", targetRole);

  if (jdText) {
    formData.append("job_description_text", jdText);
  }

  let data;

  try {
    const response = await fetch("http://127.0.0.1:8000/analyze", {
      method: "POST",
      body: formData
    });

    const rawText = await response.text();
    console.log("RAW BACKEND RESPONSE:", rawText);

    data = JSON.parse(rawText);

  } catch (err) {
    console.error("FETCH / PARSE ERROR:", err);
    alert("Failed to fetch or parse backend response. Check console.");
    return;
  }

  try {
    await renderResults(data);
    document.querySelector(".results-section")
      .scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    console.error("RENDER ERROR:", err);
    alert("Render error. Check console.");
  }
}

// -----------------------------
// Results Rendering + Chart
// -----------------------------
let roleChart = null;

async function renderResults(data) {
  const roleMatches = data.role_matches || {};

  // -------- Summary --------
  document.getElementById("resTargetRole").textContent =
    data.target_role || "-";

  document.getElementById("resRoleMatch").textContent =
    data.role_match_percentage !== undefined
      ? data.role_match_percentage + "%"
      : "N/A";

  document.getElementById("resJdMatch").textContent =
    data.jd_match_percentage !== null && data.jd_match_percentage !== undefined
      ? data.jd_match_percentage + "%"
      : "N/A";

  // -------- Target Role Lists --------
  renderList(
    "roleMissingSkillsList",
    data.role_missing_skills || [],
    "No missing skills for target role 🎉"
  );

  renderList(
    "roleExtraSkillsList",
    data.role_extra_skills || [],
    "No extra skills to remove 🎉"
  );

  // -------- Job Description Lists --------
  renderList(
    "jdMissingSkillsList",
    data.jd_missing_skills || [],
    "No missing JD skills 🎉"
  );

  renderList(
    "jdExtraSkillsList",
    data.jd_extra_skills || [],
    "No extra JD skills 🎉"
  );

  await renderRecommendedJobs(data);

  // -------- Role Match Chart --------
  const labels = Object.keys(roleMatches);
  const values = Object.values(roleMatches);

  const canvas = document.getElementById("roleChart");
  const ctx = canvas.getContext("2d");

  if (roleChart) roleChart.destroy();

  roleChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Role Match %",
        data: values,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, max: 100 }
      }
    }
  });
}

// -----------------------------
// Helper
// -----------------------------
function renderList(elementId, items, emptyText) {
  const ul = document.getElementById(elementId);
  if (!ul) return;

  ul.innerHTML = "";

  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = emptyText;
    ul.appendChild(li);
    return;
  }

  items.forEach(item => {
    const li = document.createElement("li");
    li.textContent = item;
    ul.appendChild(li);
  });
}


async function renderRecommendedJobs(data) {
  const container = document.getElementById("recommendedJobs");
  if (!container) return;

  container.innerHTML = "";

  const careerProfile = data.career_profile || {};
  const rankedRoles = Object.entries(careerProfile)
    .sort((a, b) => (b[1]?.score || 0) - (a[1]?.score || 0))
    .slice(0, 3);

  if (rankedRoles.length === 0) {
    container.textContent = "No recommendations yet. Analyze a resume first.";
    return;
  }

  for (const [role, profile] of rankedRoles) {
    const level = profile?.level || "Internship";
    const score = profile?.score ?? 0;

    const card = document.createElement("div");
    card.className = "job-card";

    const title = document.createElement("h4");
    title.textContent = role;

    const meta = document.createElement("div");
    meta.className = "job-meta";
    meta.innerHTML = `
      <span><strong>Level:</strong> ${level}</span>
      <span><strong>Career readiness:</strong> ${score}%</span>
    `;

    const links = document.createElement("div");
    links.className = "job-links";

    try {
      const response = await fetch("http://127.0.0.1:8000/job-recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role, level })
      });

      const recommendation = await response.json();
      const externalLinks = recommendation.external_links || {};

      links.innerHTML = `
        <a href="${externalLinks.linkedin || "#"}" target="_blank" rel="noopener noreferrer">LinkedIn Jobs</a>
        <a href="${externalLinks.indeed || "#"}" target="_blank" rel="noopener noreferrer">Indeed Jobs</a>
      `;
    } catch (error) {
      links.textContent = "Job links unavailable right now.";
    }

    card.appendChild(title);
    card.appendChild(meta);
    card.appendChild(links);
    container.appendChild(card);
  }
}
