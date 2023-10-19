const sound = require("sound-play");
sound.play("bowl.wav", 1).then((response) => console.log("done"));