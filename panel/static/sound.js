const SHOW = 1;
const HIDE = 0;
var TYPE = "";
var NAME = "";
var RIDDLE = 0;

var last_topic = "";
var last_track = "";

function byId(name) {
  return document.getElementById(name);
}

function S(selector) {
  return document.querySelector(selector);
}

function SA(selector) {
  return document.querySelectorAll(selector);
}

document.addEventListener("DOMContentLoaded", (event) => {
  //SETUP DROPZONE

  var myDrop = new Dropzone("#myDrop1", {
    url: `/upload_sound`,
    parallelUploads: 1,
    uploadMultiple: false,
    maxFilesize: 20,
    createImageThumbnails: false,
    thumbnailWidth: 50,
    thumbnailHeight: 50,
    init: function () {
      this.on("addedfile", function () {
        setTimeout(getSoundList, 2000);
      });
      this.on("sending", function (file, xhr, formData) {
        formData.append("type", TYPE);
        formData.append("riddle", RIDDLE);
        formData.append("old_name", NAME);
        console.log(formData);
      });
    },
    success: function (file, response) {
      S(".dz-file-preview").remove();
      S("#audio1").pause();
      S("#audio1").currentTime = null;
      // S("#npTitle").textContent = "Select sound";
      S(".dz-button").innerText = "Success - File upload";
      S(".dropzone").classList.remove("dz-started");
      S(".dz-button").innerText = "Drop mp3 file here";
    },
    accept: function (file, done) {
      if (file.name.split(".").pop() != "mp3") {
        done("You cant drop or upload only mp3 file");
      } else {
        done();
      }
    },
    chunksUploaded: function (file, response) {
      console.log("upload");
    },
  });

  //SET BUTTON LISTENER
  byId("hint").addEventListener("click", () => {
    TYPE = "hint";
    backColor("hint");
    byId("npTitle").innerText = TYPE;
    stype(HIDE);
    riddles(SHOW);
    sounds(HIDE);
  });
  byId("auto").addEventListener("click", () => {
    TYPE = "auto";
    backColor("auto");

    byId("npTitle").innerText = TYPE;
    stype(HIDE);
    riddles(SHOW);
    sounds(HIDE);
  });

  byId("action").addEventListener("click", () => {
    TYPE = "action";
    backColor("action");

    byId("npTitle").innerText = TYPE;
    stype(HIDE);
    sounds(HIDE);
    riddles(SHOW);
  });

  byId("system").addEventListener("click", () => {
    TYPE = "system";
    RIDDLE = 0;

    byId("npTitle").innerText = TYPE;
    backColor("system");
    stype(HIDE);
    riddles(HIDE);
    sounds(SHOW);
    getSoundList();
  });

  byId("back").addEventListener("click", () => {
    TYPE = "back";
    RIDDLE = 0;

    byId("npTitle").innerText = TYPE;
    backColor("back");
    stype(HIDE);
    riddles(HIDE);
    sounds(SHOW);
    getSoundList();
  });

  byId("select-sound-button").addEventListener("click", (e) => {
    byId("select-sound-button").hidden = true;
    stype(SHOW);
    riddles(HIDE);
    sounds(HIDE);
    var TYPE = "";
    var NAME = "";
    var RIDDLE = 0;
    S("#audio1").pause();
    S("#audio1").currentTime = null;
    byId("npTitle").innerText = "Please, select sound";
  });
});

function selectRiddle(num) {
  RIDDLE = num;
  S("#audio1").pause();
  S("#audio1").currentTime = null;
  // byId(`btn_${num}`).innerText;

  last_topic = byId(`btn_${num}`).innerText;
  byId("npTitle").innerText = last_topic + "/" + TYPE;
  // S("#npTitle").textContent = "Please select track"

  S(".drop-zone").style.visibility = "hidden";
  SA(".riddle-item").forEach((e) => (e.style.background = ""));
  S(`#btn_${num}`).style.background = "red";

  riddles(HIDE);
  sounds(SHOW);
  getSoundList(num);
  showSelect();
}

function showSelect() {
  byId("select-sound-button").hidden = false;
}

function getSoundList(riddle = 0) {
  // console.log(`sound/${TYPE}/${RIDDLE}`);
  if (TYPE === "auto") TYPE = "hint_auto";
  if (TYPE === "back") TYPE = "background";
  if (TYPE === "system") TYPE = "action";
  fetch(`sound/${TYPE}/${RIDDLE}`)
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      out = `<ul class='back lang_select text-i'>`;
      for (let s of data["sounds"])
        out += `<li><div class="sound-item" id='${s}' onclick="selectSound('${s}')">${s.slice(
          8,
          -4
        )}</div></li>`;
      out += `</ul>`;
      S(".sound-text").innerHTML = out;
    })
    .catch((err) => {
      console.log(err);
    });
}

function selectSound(track) {
  setRed();
  playSound(`/sound/${TYPE}/${track}`);
  NAME = track;
  showDrop();
  showSelect();
  last_track = track.slice(8, -4);
  byId("npTitle").innerText = last_topic + "/" + TYPE + "/" + last_track;

  function setRed() {
    SA(".sound-item").forEach((e) => (e.style.background = ""));
    byId(track).style.background = "red";
  }

  function playSound(track) {
    S("#audio1").src = track;
  }

  function showDrop() {
    S(".drop-zone").style.visibility = "";
    S(".dz-button").innerText = `Drop mp3 here and replace: \n ${track.slice(
      8,
      -4
    )}`;
  }
}

function backColor(id) {
  SA(".sound-type-item").forEach((e) => (e.style.background = ""));
  byId(id).style.background = "red";
}

function riddles(status) {
  SA(".riddle-item").forEach((e) => (e.style.background = ""));
  S(".riddle-body").style.display = status ? "" : "none";
}

function stype(status) {
  S(".sound-type").style.display = status ? "" : "none";
}

function sounds(status) {
  SA(".riddle-sound").forEach((e) => (e.style.background = ""));
  S(".riddle-sound").style.display = status ? "" : "none";
}

document.addEventListener("DOMContentLoaded", (e) => {
  e.preventDefault();
});
