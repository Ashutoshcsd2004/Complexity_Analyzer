const analyzeBtn = document.getElementById("analyzeBtn");
const clearBtn = document.getElementById("clearBtn");

const langSelect = document.getElementById("language");
const codeArea = document.getElementById("code");

const timeEl = document.getElementById("timeComplexity");
const spaceEl = document.getElementById("spaceComplexity");
const explanationList = document.getElementById("explanation");
const statusBadge = document.getElementById("statusBadge");

function setStatus(text, type = "secondary") {
  statusBadge.textContent = text;
  statusBadge.className = `badge bg-${type}`;
}

function setExplanation(steps) {
  explanationList.innerHTML = "";
  steps.forEach((step) => {
    const li = document.createElement("li");
    li.textContent = step;
    explanationList.appendChild(li);
  });
}

analyzeBtn.addEventListener("click", async () => {
  const language = langSelect.value;
  const code = codeArea.value.trim();

  if (!code) {
    alert("Please paste some code first!");
    return;
  }

  setStatus("Analyzing...", "info");

  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ language, code }),
    });

    if (!res.ok) {
      setStatus("Error", "danger");
      const errData = await res.json();
      alert(errData.error || "Error analyzing code");
      return;
    }

    const data = await res.json();

    timeEl.textContent = data.time_complexity || "N/A";
    spaceEl.textContent = data.space_complexity || "N/A";

    setExplanation(data.explanation_steps || ["No explanation generated."]);
    setStatus("Completed", "success");
  } catch (error) {
    console.error(error);
    setStatus("Error", "danger");
    alert("Something went wrong. Check if the Flask server is running.");
  }
});

clearBtn.addEventListener("click", () => {
  codeArea.value = "";
  timeEl.textContent = "—";
  spaceEl.textContent = "—";
  setExplanation([
    'No analysis yet. Paste code and click "Analyze Complexity".',
  ]);
  setStatus("Idle", "secondary");
});
