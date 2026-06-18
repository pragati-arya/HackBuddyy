// =========================
// Register Student
// =========================
let selectedAvatar = "avatar1.jpeg";
function selectAvatar(avatarFile){

    selectedAvatar = avatarFile;

    document.getElementById(
        "selectedAvatarPreview"
    ).src =
        "/static/avatars/" + avatarFile;

    document
        .querySelectorAll(".avatar-option")
        .forEach(avatar => {
            avatar.classList.remove(
                "avatar-selected"
            );
        });

    event.target.classList.add(
        "avatar-selected"
    );
}

async function registerUser() {

    const name = document.getElementById("name").value;
    const college = document.getElementById("college").value;
    const skills = document.getElementById("skills").value;
    const interests = document.getElementById("interests").value;
    const projectIdea = document.getElementById("projectIdea").value;
    const domain = document.getElementById("domain").value;
    const lookingFor = document.getElementById("lookingFor").value;

    try {

        const response = await fetch(
            "/register",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    college: college,
                    skills: skills,
                    interests: interests,
                    project_idea: projectIdea,
                    domain: domain,
                    looking_for: lookingFor,
                    avatar: selectedAvatar
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            alert(data.detail || "Registration Failed");
            return;
        }

        alert("✅ Student Registered Successfully");

    } catch (error) {

        console.error(error);
        alert("❌ Unable to connect to backend");
    }
}


// =========================
// Find Best Match
// =========================

async function findMatch() {

    const name = document.getElementById("searchName").value;

    try {

        const response = await fetch(`/top-match/${name}`
            
        );

        const data = await response.json();

        if (data.message) {

            document.getElementById("results").innerHTML = `
                <div class="result-box">
                    <h3>${data.message}</h3>
                </div>
            `;
            return;
        }

        const match = data.best_match;

        document.getElementById("results").innerHTML = `
            <div class="card">

                <h2>🎯 Best Match Found</h2>

                <h3>👤 ${match.name}</h3>

                <p>🏫 ${match.college}</p>

                <p>🚀 ${match.project_idea}</p>

                <p>🎯 Match Score: ${match.match_percentage}%</p>

                <p>💻 Common Skills:
                ${match.common_skills.join(", ")}</p>

                <p>❤️ Common Interests:
                ${match.common_interests.join(", ")}</p>

            </div>
        `;

    } catch (error) {

        console.error(error);

        document.getElementById("results").innerHTML = `
            <div class="result-box">
                <h3>❌ Backend Not Running</h3>
            </div>
        `;
    }
}


// =========================
// View All Matches
// =========================

async function findAllMatches() {

    const name = document.getElementById("searchName").value;

    try {

        const response = await fetch(`/match/${name}`
        );

        const data = await response.json();

        if (!data.matches) {

            document.getElementById("results").innerHTML = `
                <div class="result-box">
                    <h3>No Matches Found</h3>
                </div>
            `;

            return;
        }

        let html = `
            <div class="card">
                <h2>🏆 Top Matches</h2>
        `;

        data.matches.forEach(match => {

            html += `
                <div class="result-box">

                    <h3>👤 ${match.name}</h3>

                    <p>🏫 ${match.college}</p>

                    <p>🚀 ${match.project_idea}</p>

                    <p>🎯 Match Score:
                    ${match.match_percentage}%</p>

                    <p>💻 Common Skills:
                    ${match.common_skills.join(", ")}</p>

                    <p>❤️ Common Interests:
                    ${match.common_interests.join(", ")}</p>

                </div>

                <br>
            `;
        });

        html += "</div>";

        document.getElementById("results").innerHTML = html;

    } catch (error) {

    console.log("ERROR:", error);

    document.getElementById(
        "results"
    ).innerHTML = `
        <div class="result-box">
            <h3>❌ ${error}</h3>
        </div>
    `;
}
}


// =========================
// View Students
// =========================

async function viewStudents() {

    try {

        const response = await fetch("/students")
        ;

        const students = await response.json();

        let html = `
            <div class="card">
                <h2>👥 Registered Students</h2>
        `;

        if (students.length === 0) {

            html += `
                <div class="result-box">
                    <h3>No Students Found</h3>
                </div>
            `;

        } else {

            students.forEach(student => {

                html += `
                    <div class="result-box">

                        <div style="text-align:center;">

                            <img
                                src="/static/avatars/${student.avatar}"
                                class="student-avatar">
    

                            <h3>👤 ${student.name}</h3>

                        </div>

                        <p>college🏫 ${student.college}</p>

                        <p>skills💻 ${student.skills}</p>

                        <p>Intrests❤️ ${student.interests}</p>

                        <p>Project Idea🚀 ${student.project_idea}</p>

                        <p>Domain🌍 ${student.domain}</p>

                        <p>Looking for🔍:
                        ${student.looking_for}</p>

                    </div>

                    <br>
                `;
            });
        }

        html += "</div>";

        document.getElementById("results").innerHTML = html;

    } catch (error) {

        console.error(error);

        document.getElementById("results").innerHTML = `
            <div class="result-box">
                <h3>❌ Unable to load students</h3>
            </div>
        `;
    }
}
