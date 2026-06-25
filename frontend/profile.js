(async function () {
  const params = new URLSearchParams(window.location.search);
  const studentId = params.get("id");

  const loading = document.getElementById("loading");
  const errorEl = document.getElementById("error");
  const card = document.getElementById("profile-card");

  function showError() {
    loading.classList.add("hidden");
    errorEl.classList.remove("hidden");
  }

  function showCard() {
    loading.classList.add("hidden");
    card.classList.remove("hidden");
  }

  if (!studentId) {
    showError();
    return;
  }

  let student;
  try {
    const res = await fetch(`/profile/${studentId}`);
    if (!res.ok) {
      showError();
      return;
    }
    student = await res.json();
  } catch (err) {
    showError();
    return;
  }

  // ── Avatar ──
  const avatarEl = document.getElementById("profile-avatar");
  if (student.avatar) {
    avatarEl.src = `/static/avatars/${student.avatar}`;
  } else {
    // Fallback to initials
    avatarEl.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(student.name)}&background=6c63ff&color=fff&size=128`;
  }
  avatarEl.alt = student.name;

  // ── Basic info ──
  document.getElementById("profile-name").textContent = student.name;
  document.getElementById("profile-college").textContent = student.college;

  // ── Social buttons ──
  function setLink(btnId, url) {
    if (url && url.trim() !== "") {
      const btn = document.getElementById(btnId);
      btn.href = url.startsWith("http") ? url : `https://${url}`;
      btn.classList.remove("hidden");
    }
  }
  setLink("btn-linkedin", student.linkedin);
  setLink("btn-github", student.github);
  setLink("btn-portfolio", student.portfolio);

  // ── Tag lists ──
  function renderTags(containerId, csvString, colorClass) {
    const container = document.getElementById(containerId);
    if (!csvString || !csvString.trim()) {
      container.innerHTML = '<span class="no-data">—</span>';
      return;
    }
    container.innerHTML = csvString
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean)
      .map((s) => `<span class="tag ${colorClass}">${s}</span>`)
      .join("");
  }
  renderTags("profile-skills", student.skills, "tag-blue");
  renderTags("profile-interests", student.interests, "tag-pink");

  // ── Plain text fields ──
  function setText(id, value) {
    document.getElementById(id).textContent =
      value && value.trim() ? value : "Not specified";
  }
  setText("profile-project", student.project_idea);
  setText("profile-domain", student.domain);
  setText("profile-looking", student.looking_for);
// Set edit button link
const editBtn = document.getElementById("edit-profile-btn");
if (editBtn) editBtn.href = `/edit?id=${studentId}`;
  showCard();
})();