// =========================
// Register Student
// =========================
let selectedAvatar = "avatar1.jpeg";
function selectAvatar(avatarFile, element){

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

    element.classList.add(
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
    const linkedin = document.getElementById("linkedin").value;
    const github = document.getElementById("github").value;
    const portfolio = document.getElementById("portfolio").value;

    console.log("VALIDATION RUNNING");
    console.log("College =", college);
    console.log("Skills =", skills);
    console.log("Name =", name);
    if (
        !name.trim() ||
        !college.trim() ||
        !skills.trim()
    ){
        alert(
            "⚠️ Name, College and Skills are mandatory!"
        );
        return;
    }

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
                    avatar: selectedAvatar,
                    linkedin: linkedin,
                    github: github,
                    portfolio: portfolio,
                })
            }
        );
        console.log("Status:", response.status);

        const data = await response.json();

        console.log("Response:", data);

        if (!response.ok) {
            alert(data.detail || "Registration Failed");
            return;
        }

        alert("✅ Student Registered Successfully");

        document.getElementById("name").value = "";
        document.getElementById("college").value = "";
        document.getElementById("skills").value = "";
        document.getElementById("interests").value = "";
        document.getElementById("projectIdea").value = "";
        document.getElementById("domain").value = "";
        document.getElementById("lookingFor").value = "";
        document.getElementById("linkedin").value = "";
        document.getElementById("github").value = "";
        document.getElementById("portfolio").value = "";
        
        selectedAvatar = "avatar1.jpeg";
        
        document.getElementById(
            "selectedAvatarPreview"
        ).src = "/static/avatars/avatar1.jpeg";



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
                <div class="card">
            
                    <h2>🎯 Best Match Found</h2>
            
                    <img
                        src="/static/avatars/${match.avatar || 'avatar1.jpeg'}"
                        class="student-avatar">
            
                    <h3>👤 ${match.name}</h3>
            
                    <p>🎯 Match Score:
                    ${match.match_percentage}%</p>
            
                    <button
                        onclick="openProfile(${match.id})">
                        View Profile
                    </button>
            
                </div>
            `;
            return;
        }

        const match = data.best_match;

        document.getElementById("results").innerHTML = `
            <div class="card">

                <h2>🎯 Best Match Found</h2>
                <img
                    src="/static/avatars/${match.avatar}"
                    class="student-avatar">

                <h3>👤 ${match.name}</h3>

                

                <p>🎯 Match Score: ${match.match_percentage}%</p>

                <button
                    onclick="openProfile(${match.id})">
                    View Profile
                </button>

            </div>
        `;

    } catch (error) {

        console.error(error);

        document.getElementById("results").innerHTML = `
            <div class="result-box">
                <h3>❌ Error Occurred</h3>
                <p>${error}</p>
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
        
            <img
                src="/static/avatars/${match.avatar || 'avatar1.jpeg'}"
                class="student-avatar">
        
            <h3>👤 ${match.name}</h3>
        
            <p>🎯 Match Score:
            ${match.match_percentage}%</p>
        
            <button
                onclick="openProfile(${match.id})">
                View Profile
            </button>
        
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
                    src="/static/avatars/${student.avatar || 'avatar1.jpeg'}"
                    class="student-avatar">

                <h3>👤 ${student.name}</h3>

                <p>🏫 ${student.college}</p>

                <button
                    onclick="openProfile(${student.id})">
                    View Profile
                </button>

            </div>

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
function openProfile(studentId){

    window.location.href =
        `/profile?id=${studentId}`;
}
