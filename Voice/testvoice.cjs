const Say = require('jaxcore-say-node');
Say.speaker = require('speaker');

var voice = new Say({
	language: 'en',
	profile: 'Jack'
});

// say "hello world" through the speakers
voice.say("hello world").then(function() {
   // done
});
