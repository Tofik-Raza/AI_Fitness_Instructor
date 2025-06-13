const goalsContainer = document.getElementById('goalsContainer');
const notesContainer = document.getElementById('notesContainer');

// Add a goal
function addGoal() {
  const goal = document.getElementById('goalSelect').value;
  const tag = document.createElement('div');
  tag.className = 'tag';
  tag.innerText = goal;
  goalsContainer.appendChild(tag);
}

// Add a note
function addNote() {
  const noteInput = document.getElementById('noteInput');
  const noteText = noteInput.value.trim();
  if (!noteText) return;

  const noteDiv = document.createElement('div');
  noteDiv.style.display = 'flex';
  noteDiv.style.alignItems = 'center';
  noteDiv.style.justifyContent = 'space-around';
  noteDiv.style.gap = '8px'; // spacing between text and button

  const p = document.createElement('p');
  p.textContent = noteText;
  p.style.margin = '5px';
  p.style.height = '100%';
  p.style.width = '90%'; // remove default margin

  const btn = document.createElement('button');
  btn.textContent = 'Delete';
  btn.style.height = '100%';
  btn.style.width = '8%';
  btn.style.margin = '5px';
  btn.onclick = () => notesContainer.removeChild(noteDiv);

  noteDiv.appendChild(p);
  noteDiv.appendChild(btn);
  notesContainer.appendChild(noteDiv);
  noteInput.value = '';
}


// Generate nutrition goals from API
async function generateNutrition() {
  // alert(document.querySelector('input[name="Sex"]:checked').value);
  const userData = {
    age: parseInt(document.getElementById('age').value),
    weight: parseFloat(document.getElementById('weight').value),
    height: parseFloat(document.getElementById('height').value),
    sex: document.getElementById('sex').value,
    activity_level: document.getElementById('activity_level').value,
  };

  const response = await fetch("http://localhost:5001/api/nutrition", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData),
  });

  const data = await response.json();
  document.getElementById('calories').value = data.calories;
  document.getElementById('protein').value = data.protein;
  document.getElementById('fat').value = data.fat;
  document.getElementById('carbs').value = data.carbs;
}

// Ask AI using OLLAMA
async function askAI() {
  const askText = document.getElementById('askInput').value.trim();
  if (!askText) return;

  const notes = Array.from(notesContainer.querySelectorAll('p')).map(p => p.childNodes[0].nodeValue.trim());
  const prompt = `
You are a nutritionist AI. Based on the user's information and goals, provide a best exercise and meal.
User Info:
- age: ${document.getElementById('age').value}
- height: ${document.getElementById('height').value}g
- weight: ${document.getElementById('weight').value}g
- sex: ${document.getElementById('sex').value}g
goals:
- ${Array.from(goalsContainer.querySelectorAll('.tag')).map(tag => tag.innerText).join('\n- ')}
Notes:
- ${notes.join('\n- ')}
User Question:
${askText}
`;

    const response = await fetch("http://localhost:5000/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });

  const result = await response.json();
  document.getElementById("aiAnswer").innerText = result.response;

}
