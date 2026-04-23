// ===============================
// TIMER
// ===============================
let timeLeft = 45 * 60;

function updateTimer() {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;

    document.getElementById("timer").textContent =
        `${minutes.toString().padStart(2, "0")}:${seconds
            .toString()
            .padStart(2, "0")}`;

    if (timeLeft > 0) timeLeft--;
}

setInterval(updateTimer, 1000);

// ===============================
// ELEMENT REFERENCES
// ===============================
const codeEditor = document.getElementById("code-editor");
const submitButton = document.getElementById("submit-code");
const runButton = document.getElementById("run-code");
const outputBox = document.getElementById("output-box");
const feedbackBox = document.getElementById("feedback-box");
const languageSelect = document.querySelector(".language-select");

// ===============================
// BUTTON EVENTS
// ===============================
runButton.addEventListener("click", async () => {
    await sendCodeToBackend(false);
});

submitButton.addEventListener("click", async () => {
    await sendCodeToBackend(true);
});

// ===============================
// SEND CODE TO BACKEND
// ===============================
async function sendCodeToBackend(isFinalSubmit) {
    const code = codeEditor.value;

    if (code.trim() === "") {
        alert("Please write some code before submitting.");
        return;
    }

    const button = isFinalSubmit ? submitButton : runButton;
    button.disabled = true;
    button.textContent = isFinalSubmit ? "Submitting..." : "Running...";

    outputBox.textContent = "Executing code...\nPlease wait...";
    feedbackBox.innerHTML = "";

    try {
        const response = await fetch("http://localhost:8000/run", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                code: code,
                language: languageSelect.value.toLowerCase(),
                problem_id: 1
            })
        });

        const result = await response.json();

        displayResult(result);
        loadHistory(); // 🔥 update history

    } catch (error) {
        outputBox.textContent =
            "❌ Error connecting to backend.\nMake sure the server is running.";
    }

    button.disabled = false;
    button.textContent = isFinalSubmit ? "Submit" : "Run Code";
}

// ===============================
// DISPLAY RESULT
// ===============================
function displayResult(result) {
    let outputText = "";

    outputText += `Status: ${result.status}\n\n`;

    if (result.status === "Accepted") {
        if (result.execution_time) {
            outputText += `Execution Time: ${result.execution_time.toFixed(4)} sec\n\n`;
        }
    }

    else if (result.status === "Wrong Answer") {
        outputText += `❌ Failed Test Case: ${result["failed test case"]}\n`;
        outputText += `Expected: ${result.expected}\n`;
        outputText += `Your Output: ${result.got}\n\n`;
    }

    else if (result.status === "Runtime Error") {
        outputText += `Runtime Error:\n${result.error}`;
    }

    else if (result.status === "Compilation Error") {
        outputText += `Compilation Error:\n${result.error}`;
    }

    else if (result.status === "Time Limit Exceeded") {
        outputText += `⏱ Time Limit Exceeded`;
    }

    outputBox.textContent = outputText;

    // ===============================
    // AI FEEDBACK
    // ===============================
    if (result.feedback && result.feedback.length > 0) {
        let feedbackHTML = "";

        result.feedback.forEach(f => {
            feedbackHTML += `
                <div class="feedback-item">
                    <div class="feedback-icon suggestion">
                        <i class="fas fa-lightbulb"></i>
                    </div>
                    <div class="feedback-text">${f}</div>
                </div>
            `;
        });

        feedbackBox.innerHTML = feedbackHTML;
    } else {
        feedbackBox.innerHTML = "<p>No feedback available</p>";
    }

    updateScore(result.status);
}

// ===============================
// LOAD SUBMISSION HISTORY 🔥
// ===============================
async function loadHistory() {
    try {
        const res = await fetch("http://localhost:8000/submissions");
        const data = await res.json();

        let html = "";

        data.slice().reverse().forEach(sub => {
            html += `
                <div style="border:1px solid #ddd; padding:10px; margin:6px; border-radius:8px;">
                    <b>Status:</b> ${sub.status} <br>
                    <b>Language:</b> ${sub.language} <br>
                    <b>Problem:</b> ${sub.problem_id}
                </div>
            `;
        });

        document.getElementById("history-box").innerHTML = html;

    } catch (error) {
        console.log("History load failed");
    }
}

// ===============================
// SCORE SYSTEM
// ===============================
function updateScore(status) {
    const score = document.getElementById("score");
    const correctness = document.getElementById("correctness");
    const correctnessBar = document.getElementById("correctness-bar");

    if (!score) return;

    if (status === "Accepted") {
        score.textContent = "100";
        correctness.textContent = "100%";
        correctnessBar.style.width = "100%";
    } else {
        score.textContent = "50";
        correctness.textContent = "50%";
        correctnessBar.style.width = "50%";
    }
}

// ===============================
// LANGUAGE TEMPLATES
// ===============================
languageSelect.addEventListener("change", (e) => {
    const language = e.target.value;

    const templates = {

        python: `a, b = map(int, input().split())
print(a + b)`,

        javascript: `const input = require('fs').readFileSync(0, 'utf-8').trim();
const [a, b] = input.split(' ').map(Number);
console.log(a + b);`,

        java: `import java.util.*;
class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.println(a + b);
    }
}`,

        cpp: `#include <iostream>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    cout << a + b;
    return 0;
}`,

        c: `#include <stdio.h>

int main() {
    int a, b;
    scanf("%d %d", &a, &b);
    printf("%d", a + b);
    return 0;
}`
    };

    codeEditor.value = templates[language] || "";
});

// Load history on page load
loadHistory();