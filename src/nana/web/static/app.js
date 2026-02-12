const form = document.getElementById('chatForm');
const input = document.getElementById('message');
const chat = document.getElementById('chat');
const voiceToggle = document.getElementById('voiceToggle');
const langSelect = document.getElementById('langSelect');

function addMsg(role, text){
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.textContent = `${role === 'you' ? 'You' : 'Nana'}: ${text}`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function speak(text){
  if(!voiceToggle.checked || !window.speechSynthesis) return;
  const u = new SpeechSynthesisUtterance(text);
  u.lang = langSelect.value;
  const voices = speechSynthesis.getVoices();
  const femalePreferred = voices.find(v => /female|samantha|zira|google us english/i.test(v.name));
  if(femalePreferred) u.voice = femalePreferred;
  speechSynthesis.cancel();
  speechSynthesis.speak(u);
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if(!message) return;
  addMsg('you', message);
  input.value = '';

  const res = await fetch('/api/chat', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({message, lang: langSelect.value})
  });
  const data = await res.json();
  addMsg('nana', data.reply);
  speak(data.reply);
});

addMsg('nana', 'I am awake. I know current time/date context and I keep growing each interaction.');
