const sound = require("sound-play");
const { getAudioDurationInSeconds } = require('get-audio-duration')

const path = require("path");
filePath = path.join(__dirname, "sounds\\kitchen voice\\put1.wav");
console.log(filePath)
sound.play(filePath);

filePath2 = path.join(__dirname, "sounds\\kitchen voice\\onehalfmeasurecup.wav");
duration1 = 0;
duration2 = 0;
getAudioDurationInSeconds(filePath).then((duration1) => {
  duration1 = duration1 * 1000 + 1
  console.log(duration1)
  setTimeout(function() {
  sound.play(filePath2);
  }, duration1);
  
})

filePath3 = path.join(__dirname, "sounds\\kitchen voice\\put2.wav");
filePath4 = path.join(__dirname, "sounds\\kitchen voice\\alright.wav");

getAudioDurationInSeconds(filePath2).then((duration2) => {
getAudioDurationInSeconds(filePath).then((duration1) => {
getAudioDurationInSeconds(filePath3).then((duration3) => {
  duration1 = duration1 * 1000 + 1
  duration2 = duration2 * 1000 + 1
  duration3 = duration3 * 1000 + 1
  duration2 = duration1 + duration2
  duration3 = duration3 + duration2
  setTimeout(function() {
  sound.play(filePath3);
  }, duration2);
  console.log(duration1)

  setTimeout(function() {
  sound.play(filePath4);
  }, duration3 + 1000);
  console.log(duration1)
  
})
})
})

