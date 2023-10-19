const sound = require("sound-play");

const path = require("path");
const filePath = path.join(__dirname, "bowl.wav");
sound.play(filePath);