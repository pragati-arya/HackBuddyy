(async function () {
  const params    = new URLSearchParams(window.location.search);
  const studentId = params.get("id");

  // Set back button href
  document.getElementById("back-btn").href    = `/profile?id=${studentId}`;
  document.getElementById("cancel-btn").href  = `/profile?id=${studentId}`;

  if (!studentId) {
    window.location.href = "/";
    return;
  }

  // ── Load student data ──────────────────────────────────
  let student;
  try {
    const res = await fetch(`/profile/${studentId}`);
    if (!res.ok) { window.location.href = "/"; return; }
    student = await res.json();
  } catch {
    window.location.href = "/";
    return;
  }

  // ── Avatars list ───────────────────────────────────────
  const AVATARS = [
    "avatar1.jpeg","avatar2.jpeg","avatar3.jpeg","avatar4.jpeg",
    "avatar5.jpeg","avatar6.jpeg","avatar7.jpeg","avatar8.jpeg",
    "avatar9.jpeg","avatar10.jpeg","avatar11.jpeg","avatar12.jpeg"
  ];

  let selectedAvatar = student.avatar || AVATARS[0];
  let verifiedName   = "";

  // ── STEP 1: Identity verification ─────────────────────
  const verifyBtn   = document.getElementById("verify-btn");
  const verifyInput = document.getElementById("verify-name");
  const verifyError = document.getElementById("verify-error");
  const stepVerify  = document.getElementById("step-verify");
  const stepEdit    = document.getElementById("step-edit");

  verifyBtn.addEventListener("click", () => {
    const typed = verifyInput.value.trim();
    if (typed.toLowerCase() === student.name.toLowerCase()) {
      verifiedName = student.name;
      verifyError.classList.add("hidden");
      stepVerify.classList.add("hidden");
      stepEdit.classList.remove("hidden");
      populateForm();
    } else {
      verifyError.classList.remove("hidden");
      verifyInput.classList.add("shake");
      setTimeout(() => verifyInput.classList.remove("shake"), 500);
    }
  });

  verifyInput.addEventListener("keydown", e => {
    if (e.key === "Enter") verifyBtn.click();
  });

  // ── STEP 2: Populate form ──────────────────────────────
  function populateForm() {
    document.getElementById("edit-name-display").textContent = student.name;

    // Avatar preview
    updateAvatarPreview(selectedAvatar);

    // Build avatar grid
    const grid = document.getElementById("avatar-grid");
    AVATARS.forEach(av => {
      const wrapper = document.createElement("div");
      wrapper.className = "av-item" + (av === selectedAvatar ? " av-selected" : "");
      wrapper.innerHTML = `<img src="/static/avatars/${av}" alt="${av}"/>`;
      wrapper.addEventListener("click", () => {
        selectedAvatar = av;
        document.querySelectorAll(".av-item").forEach(el => el.classList.remove("av-selected"));
        wrapper.classList.add("av-selected");
        updateAvatarPreview(av);
      });
      grid.appendChild(wrapper);
    });

    // Fill fields
    document.getElementById("f-college").value   = student.college   || "";
    document.getElementById("f-skills").value    = student.skills    || "";
    document.getElementById("f-interests").value = student.interests || "";
    document.getElementById("f-project").value   = student.project_idea || "";
    document.getElementById("f-domain").value    = student.domain    || "";
    document.getElementById("f-looking").value   = student.looking_for || "";
    document.getElementById("f-linkedin").value  = student.linkedin  || "";
    document.getElementById("f-github").value    = student.github    || "";
    document.getElementById("f-portfolio").value = student.portfolio || "";
  }

  function updateAvatarPreview(av) {
    const img = document.getElementById("edit-avatar-preview");
    img.src = `/static/avatars/${av}`;
  }

  // ── Save ───────────────────────────────────────────────
  document.getElementById("save-btn").addEventListener("click", async () => {
    const saveBtn     = document.getElementById("save-btn");
    const saveError   = document.getElementById("save-error");
    const saveSuccess = document.getElementById("save-success");

    const skills = document.getElementById("f-skills").value.trim();
    if (!skills) {
      saveError.textContent = "❌ Skills cannot be empty.";
      saveError.classList.remove("hidden");
      return;
    }

    saveBtn.textContent = "Saving…";
    saveBtn.disabled    = true;
    saveError.classList.add("hidden");
    saveSuccess.classList.add("hidden");

    const payload = {
      confirm_name: verifiedName,
      college:      document.getElementById("f-college").value.trim(),
      skills:       skills,
      interests:    document.getElementById("f-interests").value.trim(),
      project_idea: document.getElementById("f-project").value.trim(),
      domain:       document.getElementById("f-domain").value.trim(),
      looking_for:  document.getElementById("f-looking").value.trim(),
      avatar:       selectedAvatar,
      linkedin:     document.getElementById("f-linkedin").value.trim(),
      github:       document.getElementById("f-github").value.trim(),
      portfolio:    document.getElementById("f-portfolio").value.trim(),
    };

    try {
      const res = await fetch(`/profile/${studentId}`, {
        method:  "PUT",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok) {
        saveSuccess.classList.remove("hidden");
        saveBtn.textContent = "✅ Saved!";
        setTimeout(() => {
          window.location.href = `/profile?id=${studentId}`;
        }, 1200);
      } else {
        saveError.textContent = "❌ " + (data.detail || "Something went wrong.");
        saveError.classList.remove("hidden");
        saveBtn.textContent = "💾 Save Changes";
        saveBtn.disabled    = false;
      }
    } catch {
      saveError.textContent = "❌ Network error. Please try again.";
      saveError.classList.remove("hidden");
      saveBtn.textContent = "💾 Save Changes";
      saveBtn.disabled    = false;
    }
  });
})();