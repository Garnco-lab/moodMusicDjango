// using dev mozilla base to translate the original python script

var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
var SpeechGrammarList = window.SpeechGrammarList || window.webkitSpeechGrammarList
var SpeechRecognitionEvent = window.SpeechRecognitionEvent || window.webkitSpeechRecognitionEvent

let moods = ['sad', 'angry', 'happy', 'cheese']
let grammar = '#JSGF V1.0; grammar moods; public <mood> = ' + moods.join(' | ') + ' ;'

let recognition = new SpeechRecognition();
let speechRecognitionList = new SpeechGrammarList();
speechRecognitionList.addFromString(grammar, 1);
console.log(speechRecognitionList);
recognition.grammars = speechRecognitionList;
recognition.continuous = false;
recognition.lang = 'en-US';
recognition.interimResults = false;
recognition.maxAlternatives = 1;

let diagnostic = document.querySelector('.output');
let bg = document.querySelector('html');
let hints = document.querySelector('.brain_desc');

let colorHTML= '';
moods.forEach(function(v, i, a){
  console.log(v, i);
  colorHTML += '<span style="background-color:' + v + ';"> ' + v + ' </span>';
});



document.body.onclick = function() {
  recognition.start();

  console.log('Ready to receive a color command.');

  document.getElementById('brain_desc').innerHTML = 'Ask me to play a song thats happy or sad';

}

recognition.onresult = function(event) {
  let color = event.results[0][0].transcript;
  // diagnostic.textContent = 'Result received: ' + color + '.';
  // bg.style.backgroundColor = color;
  console.log('Confidence: ' + event.results[0][0].confidence, color);
  document.getElementById('brain_desc').innerHTML = 'Okay let me think about that...';
  location.href = "/" + "musicBackEnd";
}

recognition.onspeechend = function() {
  recognition.stop();
}

recognition.onnomatch = function(event) {
  diagnostic.textContent = "I didn't recognise that color.";
}

recognition.onerror = function(event) {
  diagnostic.textContent = 'Error occurred in recognition: ' + event.error;
}
