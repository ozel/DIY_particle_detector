/*
This HTML/js web browser user interface utilizes the Web Audio API (https://www.w3.org/TR/webaudio/)
which allows to record raw audio frames (@48 kHz in 16bit PCM format) from an audio/microphone input 
via a web browser.
The trigger threshold can be set with 2 buttons, '+'/'-' and up/down arrow keys or by swiping up/down 
on the waveform area. 
The recorded data is saved into a file using the the MessagePack format for further pulse 
processing by the analyse_and_plot_pulses.py python script.

Due to varrying browser implementations of the Web Audio API, some differences apply:
  - A sample rate of 48 kHz cannot yet be configured by every browser (https://developer.mozilla.org/en-US/docs/Web/API/AudioContextOptions/sampleRate)
    Safari on iOS uses 48 kHz as default, Chrome accepts the setting in recent versions (tested with Chrome 75)
    Firefox should support it since version 61 on most desktop platforms (seems not yet the case on mac OS)
  - The Safari browser does not yet support getFloatTimeDomainData() (https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode/getFloatTimeDomainData)
    a workaround implementation was used which could impact the accuracy of data in case of spectral analyses.
  - Not all browsers retain the generated file name for the saved data file (includes timestamp and number of waveforms for convenience).

List of preferred browsers for this software (as of July 2019): 
Chrome (mobile and desktop), Firefox (depends on OS). Safari on iOS.

Author: Oliver Keller
Date: July 2019

Javascript libraries:
  - FileSaver.js helper function https://github.com/eligrey/FileSaver.js
  - minimal MessagePack implementation msgpack.js https://github.com/ygoe/msgpack.js

The oscilloscope canvas code is based on this example: https://github.com/mathiasvr/audio-oscilloscope

Todo:
  - implement fixed horizontal trigger point (currently triggers occur allong whole x-axis)
  - display threshold value as number input and add coarse value modifier buttons/keys
*/



function webAudioTouchUnlock(context) {
  return new Promise(function(resolve, reject) {
    if (context.state === "suspended" && "ontouchstart" in window) {
      var unlock = function() {
        context.resume().then(
          function() {
            document.body.removeEventListener("touchstart", unlock);
            document.body.removeEventListener("touchend", unlock);

            resolve(true);
          },
          function(reason) {
            reject(reason);
          }
        );
      };

      document.body.addEventListener("touchstart", unlock, false);
      document.body.addEventListener("touchend", unlock, false);
    } else {
      resolve(false);
    }
  });
}

// credit: http://www.javascriptkit.com/javatutor/touchevents2.shtml
function swipedetect(el, callback) {
  var touchsurface = el,
    swipedir,
    startX,
    startY,
    distX,
    distY,
    threshold = 150, //required min distance traveled to be considered swipe
    restraint = 100, // maximum distance allowed at the same time in perpendicular direction
    allowedTime = 300, // maximum time allowed to travel that distance
    elapsedTime,
    startTime,
    handleswipe = callback || function(swipedir) {};

  touchsurface.addEventListener(
    "touchstart",
    function(e) {
      var touchobj = e.changedTouches[0];
      swipedir = "none";
      dist = 0;
      startX = touchobj.pageX;
      startY = touchobj.pageY;
      startTime = new Date().getTime(); // record time when finger first makes contact with surface
      e.preventDefault();
    },
    false
  );

  touchsurface.addEventListener(
    "touchmove",
    function(e) {
      e.preventDefault(); // prevent scrolling when inside DIV
    },
    false
  );

  touchsurface.addEventListener(
    "touchend",
    function(e) {
      var touchobj = e.changedTouches[0];
      distX = touchobj.pageX - startX; // get horizontal dist traveled by finger while in contact with surface
      distY = touchobj.pageY - startY; // get vertical dist traveled by finger while in contact with surface
      elapsedTime = new Date().getTime() - startTime; // get time elapsed
      if (elapsedTime <= allowedTime) {
        // first condition for awipe met
        if (Math.abs(distX) >= threshold && Math.abs(distY) <= restraint) {
          // 2nd condition for horizontal swipe met
          swipedir = distX < 0 ? "left" : "right"; // if dist traveled is negative, it indicates left swipe
        } else if (
          Math.abs(distY) >= threshold &&
          Math.abs(distX) <= restraint
        ) {
          // 2nd condition for vertical swipe met
          swipedir = distY < 0 ? "up" : "down"; // if dist traveled is negative, it indicates up swipe
        }
      }
      handleswipe(swipedir);
      e.preventDefault();
    },
    false
  );
}

class Oscilloscope {
  constructor(source, options = {}) {
    if (!(source instanceof window.AudioNode)) {
      throw new Error("Oscilloscope source must be an AudioNode");
    }

    if (source instanceof window.AnalyserNode) {
      this.analyser = source;
    } else {
      this.analyser = source.context.createAnalyser();
      source.connect(this.analyser);
    }

    //if (options.fftSize) { this.analyser.fftSize = options.fftSize }
    this.analyser.fftSize = 4096 / 2;
    this.analyser.smoothingTimeConstant = 0;
    this.timeDomain = new Uint8Array(this.analyser.fftSize); //this.analyser.frequencyBinCount);
    this.samples = new Float32Array(this.analyser.fftSize);
    this.drawRequest = 0;
    this.width = 0
    this.height = 0
    this.threshold = -13000;
    this.alpha_threshold = -1243000; //disabled
    this.data = [];
    this.downloadBlob = null;
    this.lastTime = null;
    this.startTime = new Date();
    this.waveforms = 0;
    this.alphas = 0;
    this.electrons = 0;
  }

  // begin default signal animation
  setThreshold(threshold) {
    this.threshold = this.threshold + threshold;
    this.ctx.beginPath();
    this.ctx.clearRect(this.x0 +1, this.y0, this.ctx.canvas.width, this.ctx.canvas.height);
    this.ctx.stroke();

    console.log(this.threshold);
  }
  animate(ctx, x0, y0, width, height) {
    if (this.drawRequest) {
      throw new Error("Oscilloscope animation is already running");
    }
    this.ctx = ctx;
    this.width = width;
    this.height = height;
    this.x0 = x0
    this.y0 = y0

    // draw left y-axis for reference
    ctx.beginPath();
    ctx.strokeStyle = "#ffffff";

    ctx.moveTo(x0, y0);
    ctx.lineTo(x0, height);
    ctx.stroke();
      
    const drawLoop = () => {
      //ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height)

      this.draw(ctx, x0, y0, width, height);
      this.update_time();
      this.update_stats();

      this.drawRequest = window.requestAnimationFrame(drawLoop);
    };
    drawLoop();
  }

  // stop default signal animation
  stop() {
    if (this.drawRequest) {
      window.cancelAnimationFrame(this.drawRequest);
      this.drawRequest = 0;
      this.ctx.clearRect(x0+1, y0, this.ctx.canvas.width, this.ctx.canvas.height);
    }
  }

  update_time() {
    var now = new Date();
    var elapsed = now.valueOf() - this.startTime.valueOf(); // time in milliseconds
    var dateDiff = new Date(elapsed);
    var h = dateDiff.getHours() - 1;
    var h = h.toString().padStart(2, "0");
    var m = dateDiff
      .getMinutes()
      .toString()
      .padStart(2, "0");
    var s = dateDiff
      .getSeconds()
      .toString()
      .padStart(2, "0");
    document.getElementById("time").innerHTML = h + ":" + m + ":" + s;
  }

  update_stats() {
    document.getElementById("statistic").innerHTML =
      "sum: " +
      this.waveforms +
      "  &emsp;&emsp;&emsp;  e&#8315;: " +
      this.electrons +
      "&emsp;&emsp;&emsp;   &alpha;: " +
      this.alphas;
  }
  // draw signal
  draw(
    ctx,
    x0 = 0,
    y0 = 0,
    width = ctx.canvas.width - x0,
    height = ctx.canvas.height - y0
  ) {
    this.analyser.getByteTimeDomainData(this.timeDomain);

    //workaround for missing getFloatTimeDomainData() in Safari
    if (this.analyser && typeof this.analyser.getFloatTimeDomainData == "undefined") {
      //console.log("No native support for analyser.getFloatTimeDomainData()")
      //if(this.timeDomain.length !=  this.samples.length) {
        //console.log("array length missmatch, this.timeDomain:", this.timeDomain.length, " this.samples:", this.samples.length)
      //}
      this.analyser.getByteTimeDomainData(this.timeDomain);
      // scales unsigned 8 bit to signed 16 bit... introduces quantisation errors!
      for (var i = 0, imax = this.samples.length; i < imax; i++) {
        this.samples[i] = (this.timeDomain[i] - 128) * 0.0078125;
      }
      // code from https://github.com/mohayonao/get-float-time-domain-data
      // var uint8 = new Uint8Array(2048);
      // global.AnalyserNode.prototype.getFloatTimeDomainData = function(array) {
      //  this.getByteTimeDomainData(uint8);
      //  for (var i = 0, imax = array.length; i < imax; i++) {
      //    array[i] = (uint8[i] - 128) * 0.0078125;
      //}
    } else {
      this.analyser.getFloatTimeDomainData(this.samples);
    }
    // }

    // if (typeof this.analyser.getFloatTimeDomainData == "undefined") {
    //   // replacement from https://github.com/mohayonao/get-float-time-domain-data
    //   //getFloatTimeDomainData(this.samples);
    // }
    
    const x_scale = 1;
    const step = width / this.samples.length * x_scale;
    const y_scale = 1;

    var min = this.samples.reduce((a, b) => Math.min(a, b));
    // samples range is -1 to +1, FIXME: web-audio API should provide internal/native sample resolution
    min = min * Math.pow(2, 15); //16 bit signed pcm / 2 = 2^15

    if (min < this.threshold) {
      var now = new Date();
      var PCM16b = new Int16Array(
        this.samples.map(function(element) {
          return element * Math.pow(2, 15);
        }).buffer
      );
      var waveform = {};
      waveform["ts"] = now.valueOf();
      waveform["pulse"] = Array.from(PCM16b);
      this.data[this.waveforms] = waveform;
      this.waveforms += 1;
      this.lastTime = now;
      ctx.beginPath();
      ctx.clearRect(x0+1, y0, ctx.canvas.width, ctx.canvas.height);
      //ctx.moveTo(x0, y0);
      //console.log(this.samples[0],this.samples[1])
      ctx.strokeStyle = "#ffffff";

      // drawing loop
      var oldy = y0 + height / 2;
      ctx.moveTo(x0, oldy);
      for (let i = 0; i < this.samples.length; i += step) {
        const percent = this.samples[i] * y_scale
        const x = x0 + i * step;
        const y = y0 + height / 2 + this.samples[i] * -1 * height / 2;
        ctx.lineTo(x, oldy);
        ctx.lineTo(x, y);
        oldy = y;
      }
      ctx.stroke();
      if (min < this.alpha_threshold) {
        this.alphas += 1;
        console.log(min, "alpha");
      } else {
        this.electrons += 1;
        console.log(min, "electron");
      }
    }
    // threshold line
    ctx.beginPath();
    ctx.strokeStyle = "red";
    //ctx.moveTo(x0,y0)
    ctx.moveTo(
      x0+1,
      y0 + height / 2 + -1 * this.threshold * y_scale * height / 2 / Math.pow(2, 15)
    );
    ctx.lineTo(
      x0 + width,
      y0 + height / 2 + -1 * this.threshold * y_scale * height / 2 / Math.pow(2, 15)
    );
    ctx.stroke();
  }
}

// shim
//navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia ||
//                         navigator.mozGetUserMedia || navigator.msGetUserMedia ||
//                         navigator.mediaDevices.getUserMedia

var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioCtx = new AudioContext({  sampleRate: 48000}); 


webAudioTouchUnlock(audioCtx).then(
  function(unlocked) {
    if (unlocked) {
      console.log("audioCtx unlocked");
      // AudioContext was unlocked from an explicit user action,
      // sound should start playing now
    } else {
      console.log("audioCtx was already unlocked");
      // There was no need for unlocking, devices other than iOS
    }
  },
  function(reason) {
    console.error(reason);
  }
);


// setup canvas

var canvas =  document.createElement("canvas");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
//document.body.appendChild(canvas);
document.getElementById("pulse_scope").appendChild(canvas)

swipedetect(canvas, function(swipedir) {
  // swipedir contains either "none", "left", "right", "top", or "down"
  console.log(swipedir);
  if (swipedir == "up") {
    scope.setThreshold(-100)
    console.log("up")
  } else if (swipedir == "down") {
    scope.setThreshold(100)
    console.log("down")
  }
});

// customize drawing options
var ctx = canvas.getContext("2d");
ctx.lineWidth = 2;
ctx.font = "20px monospace";
ctx.fillStyle = "orange";
ctx.fillText("Waiting for audio input... please allow microphone usage.", 80, 160);
ctx.fillText("Hit the 'reset' button if waveforms do not appear automatically.", 80, 190);
ctx.strokeStyle = "#ffffff";


// get user microphone
var constraints = { video: false, audio: true };
function errorCallback(error) {
  console.log("navigator.getUserMedia error: ", error);
  //if (error ==  "DOMException: \"Operation is not supported\"") {
    console.log("Cannot set sample rate to 48000? Not yet implemented in all browsers.")
    audioCtx = new AudioContext();  
  //}
  // TRY AGAIN...
  navigator.mediaDevices
  .getUserMedia(constraints)
  .then(streamCallback)
  .catch(errorCallback);
}

var scope = null

function streamCallback(stream) {
  var source = audioCtx.createMediaStreamSource(stream);

  // attach oscilloscope
  scope = new Oscilloscope(source);

  // start default animation loop
  scope.animate(ctx, 10, 0, 1024, 600);


  var rate = "?"
  if (typeof audioCtx.sampleRate == "number") {
        // replacement from https://github.com/mohayonao/get-float-time-domain-data
        rate = audioCtx.sampleRate
  }

  document.getElementById("rate").innerHTML = "sample rate:<br> " + rate/1000 + " kHz";
}

navigator.mediaDevices
  .getUserMedia(constraints)
  .then(streamCallback)
  .catch(errorCallback);

document.getElementById("saveData").addEventListener("click", function(e) {
    //var text = document.getElementById('source').innerHTML;
    //var file = new File([text], "hello world.txt", {type: "text/plain;charset=utf-8"});
    // save messagepack object as binary blob it
    if (scope.waveforms > 0) {
      var bytes = msgpack.serialize(scope.data);
      var blob = new Blob([bytes], { type: "octet/stream" });
      //saveAs(blob,"data.dat");
      console.log(JSON.stringify(scope.data));
      var date =
        scope.lastTime.getFullYear() +
        "-" +
        (scope.lastTime.getMonth() + 1).toString().padStart(2, "0") +
        "-" +
        scope.lastTime
          .getDate()
          .toString()
          .padStart(2, "0");
      var time =
        scope.lastTime
          .getHours()
          .toString()
          .padStart(2, "0") +
        "-" +
        scope.lastTime
          .getMinutes()
          .toString()
          .padStart(2, "0");
      saveAs(blob, "DIY_Particle_Detector_"
             + scope.waveforms + "-pulses_" + date + "_" + time + ".msgp");
      //saveAs(blob, "test.msgp");
    }
  });

  document.getElementById("reset").addEventListener("click", function(e) {
    scope.data = [];
    scope.downloadBlob = null;
    scope.lastTime = null;
    scope.startTime = new Date();
    scope.waveforms = 0;
    scope.alphas = 0;
    scope.electrons = 0;

    scope.update_time();
    scope.update_stats();
    audioCtx.resume().then(() => {
      console.log('audioContext resumed successfully');
    });

  });

  document.getElementById("thlUp").addEventListener("click", function(e) {
    scope.setThreshold(1000);
  });

  document.getElementById("thlDown").addEventListener("click", function(e) {
    scope.setThreshold(-1000);
  });

  function checkKey(e) {
    e = e || window.event;
    if (e.key == "+" || e.key == "ArrowUp") {
      scope.setThreshold(100);
    } else if (e.key == "-" || e.key == "ArrowDown") {
      // down arrow
      scope.setThreshold(-100);
    }
  }
  //this.ctx.addEventListener('keydown',checkKey,false);
  document.onkeydown = checkKey;

