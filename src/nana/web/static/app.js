const form = document.getElementById('chatForm');
const input = document.getElementById('message');
const chat = document.getElementById('chat');
const voiceOutToggle = document.getElementById('voiceOutToggle');
const voiceInToggle = document.getElementById('voiceInToggle');
const voiceBtn = document.getElementById('voiceBtn');
const langSelect = document.getElementById('langSelect');

let recognition = null;
let listening = false;

function addMsg(role, text){
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.textContent = `${role === 'you' ? 'You' : 'Nana'}: ${text}`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function speak(text){
  if(!voiceOutToggle.checked || !window.speechSynthesis) return;
  const u = new SpeechSynthesisUtterance(text);
  u.lang = langSelect.value;
  const voices = speechSynthesis.getVoices();
  const femalePreferred = voices.find(v => /female|samantha|zira|google us english/i.test(v.name));
  if(femalePreferred) u.voice = femalePreferred;
  speechSynthesis.cancel();
  speechSynthesis.speak(u);
}

async function sendMessage(message){
  addMsg('you', message);
  const res = await fetch('/api/chat', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({message, lang: langSelect.value})
  });
  const data = await res.json();
  addMsg('nana', data.reply);
  speak(data.reply);
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = input.value.trim();
  if(!message) return;
  input.value = '';
  await sendMessage(message);
});

function setupRecognition(){
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SpeechRecognition) {
    voiceBtn.disabled = true;
    voiceBtn.textContent = '🎙 Unsupported';
    return;
  }
  recognition = new SpeechRecognition();
  recognition.lang = langSelect.value;
  recognition.continuous = true;
  recognition.interimResults = false;

  recognition.onresult = async (event) => {
    const last = event.results[event.results.length - 1];
    const transcript = last[0].transcript.trim();
    if(transcript) await sendMessage(transcript);
  };

  recognition.onend = () => {
    if(listening && voiceInToggle.checked) {
      recognition.lang = langSelect.value;
      recognition.start();
    }
  };
}

voiceBtn.addEventListener('click', () => {
  if(!recognition) return;
  listening = !listening;
  if(listening) {
    recognition.lang = langSelect.value;
    recognition.start();
    voiceBtn.textContent = '🛑 Stop Listening';
    voiceInToggle.checked = true;
  } else {
    recognition.stop();
    voiceBtn.textContent = '🎙 Start Listening';
    voiceInToggle.checked = false;
  }
});

voiceInToggle.addEventListener('change', () => {
  if(!recognition) return;
  if(voiceInToggle.checked && !listening) {
    listening = true;
    recognition.lang = langSelect.value;
    recognition.start();
    voiceBtn.textContent = '🛑 Stop Listening';
  }
  if(!voiceInToggle.checked && listening) {
    listening = false;
    recognition.stop();
    voiceBtn.textContent = '🎙 Start Listening';
  }
});

langSelect.addEventListener('change', () => {
  if(recognition && listening) {
    recognition.stop();
    recognition.lang = langSelect.value;
    recognition.start();
  }
});

setupRecognition();
addMsg('nana', 'signal ready');
