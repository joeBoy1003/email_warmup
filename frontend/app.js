const baseURL = "http://127.0.0.1:5000";

// Add Email Account
document.getElementById("addAccountForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value;
    const provider = document.getElementById("provider").value;
    const smtpServer = document.getElementById("smtpServer").value;
    const port = document.getElementById("port").value;
    const password = document.getElementById("password").value;

    const response = await fetch(`${baseURL}/add_account`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, provider, smtp_server: smtpServer, port, password }),
    });
    const result = await response.json();
    alert(result.message);
});

// Set Schedule
document.getElementById("scheduleForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("scheduleEmail").value;
    const dailyLimit = document.getElementById("dailyLimit").value;

    const response = await fetch(`${baseURL}/set_schedule`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, daily_limit: dailyLimit }),
    });
    const result = await response.json();
    alert(result.message);
});

// Upload Recipients
document.getElementById("recipientUploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = document.getElementById("recipientFile").files[0];
    const email = prompt("Enter the email account for these recipients:");
    const formData = new FormData();
    formData.append("email", email);
    formData.append("file", file);

    const response = await fetch(`${baseURL}/recipients/upload`, {
        method: "POST",
        body: formData,
    });
    const result = await response.json();
    alert(result.message);
});

// Fetch Analytics
async function fetchAnalytics() {
    const response = await fetch(`${baseURL}/analytics`);
    const data = await response.json();
    const list = document.getElementById("analyticsList");
    list.innerHTML = "";
    data.forEach((entry) => {
        const listItem = document.createElement("li");
        listItem.textContent = `${entry.email}: Sent ${entry.sent}, Spam ${entry.spam}, Replies ${entry.replies}`;
        list.appendChild(listItem);
    });
}
setInterval(fetchAnalytics, 5000);  // Update every 5 seconds
