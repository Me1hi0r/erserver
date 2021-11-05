var c = 1; //counter for len table

function S(selector) {
  return document.querySelector(selector);
}

function byId(name) {
  return document.getElementById(name);
}

function byName(name) {
  return document.getElementsByName(name)[0];
}

function len(c) {
  return byId("table").children[1].children.length + c;
}

function sound_slider(num) {
  S(`#riddle-${num}-sound-button-label`).innerText =
    "" + S(`#riddle-${num}-sound`).value;
}

function video_slider(num) {
  // console.log(S(`#riddle-${num}-video`))
  S(`#riddle-${num}-video-button-label`).innerText =
    "" + S(`#riddle-${num}-video`).value;
}

function auto_slider(num) {
  let value = S(`#riddle-${num}-auto`).value;
  S(`#riddle-${num}-auto-button-label`).innerText = "" + value;
  let div = document.createElement("div");
  let block = S(`#riddle-${num}-auto-inputs`);
  div.innerHTML = `${value}:<input class="inp auto" name="riddle-${num}-autoi-${value}" value="0">`;
  // console.log(block.children.length)
  if (value == 0) {
    while (block.firstChild) {
      block.removeChild(block.firstChild);
    }
  } else {
    block.children.length <= value
      ? block.appendChild(div)
      : block.removeChild(block.children[block.children.length - 1]);
  }
}

function show_all() {
  all = document.getElementsByClassName("auto-hints");
  for (let a of all) {
    if (a.value != "0") {
      [_, num, _] = a.id.split("-");
      block = byId(`riddle-${num}-auto-inputs`);
      list_args = block.attributes[2].value.split(",");
      // console.log(all, num, a.id, d, v);
      let c = 0;
      for (let a of list_args) {
        c++;
        let div = document.createElement("div");
        div.innerHTML = `${c}:<input class="inp auto" name="riddle-${num}-autoi-${c}" value="${a}">`;
        block.appendChild(div);
      }
    }
  }
}

function show_selected(name) {
  let s = byName(name);
  s.children[s.attributes["value"].value].selected = true;
}

function show_auto(block, num, args) {
  let list_args = args.split(",");
  // let block = S(`#riddle-${num}-auto-inputs`);
  let c = 0;
  for (let a of list_args) {
    c++;
    let div = document.createElement("div");
    div.innerHTML = `${c}:<input class="inp auto" name="riddle-${num}-autoi-${c}" value="${a}">`;
    block.appendChild(div);
  }
}

var MQTT_ADDR = "192.168.10.1";
var MQTT_PORT = 8080;
var clientId = "id_" + parseInt(Math.random() * 1000, 10);
var client = new Messaging.Client(MQTT_ADDR, MQTT_PORT, clientId);

var topic = ["/erp/config"];

var options = {
  timeout: 3,
  onSuccess: () => {
    console.log(
      "MQTT: Connected: " + MQTT_ADDR + ":" + MQTT_PORT + ", id: " + clientId
    );
    topic.forEach((e) => {
      mqtt_subscribe(e);
      console.log("MQTT: Subscribed: " + e);
    });
    console.log("SUCCES");
  },
  onFailure: (message) => {
    console.log(
      "Error: MQTT: Connection: " +
        MQTT_ADDR +
        ":" +
        MQTT_PORT +
        ": " +
        message.errorMessage
    );
  },
};

client.onConnectionLost = function (responseObject) {
  // alert("Connection lost: Please, press OK, and wait for reboot (" + responseObject.errorMessage + ")");
  // location.reload();
};

client.onMessageArrived = function (message) {
  console.log(
    "MQTT: Topic: " +
      message.destinationName +
      ", Data: " +
      message.payloadString
  );
};

function mqtt_publish(payload, topic, _qos) {
  if (typeof _qos == "undefined") _qos = 2;
  var message = new Messaging.Message(payload);
  message.destinationName = topic;
  message.qos = _qos;
  client.send(message);
}

function mqtt_subscribe(topic, _qos) {
  if (typeof _qos == "undefined") _qos = 2;
  client.subscribe(topic, {
    qos: _qos,
  });
}

function mqtt_connect() {
  console.log("connect");
  client.connect(options);
}

// byId('new-quest-button').addEventListener('click', (e) => {})
document.addEventListener("DOMContentLoaded", (e) => {
  e.preventDefault();

  //START MQTT
  mqtt_connect();
  console.log("mqtt-connect");

  byId("sel-quest").addEventListener("change", (e) => {
    let name = e.srcElement.value;
    if (name == "NEW QUEST") {
      byId("new-quest-block").hidden = false;
    } else if (name != "0") {
      console.log("load configuration");
      byId("load-quest-button").hidden = false;
    }
  });
  byId("load-quest-button").addEventListener("click", (e) => {
    e.preventDefault();
    i = document.createElement("input");
    i.hidden = true;
    i.name = "load-quest-name";
    i.value = byId("sel-quest").selectedOptions[0].value;
    console.log(i);

    byId("main-form").appendChild(i);
    byId("main-form").action = "/config/load";
    byId("main-form").submit();
  });
  byId("btnReset").addEventListener("click", (e) => {
    e.preventDefault();
    alert(
      "If you push OK button, you delete all custom sound !!! Press close tab if you don't want to delete music"
    );
    byId("main-form").action = "/sound/reset";
    byId("main-form").submit();
  });

  byName("start_offset").addEventListener("input", (e) => {
    let val = e.srcElement.value;
    byId("time-start-label").innerText =
      val == 0
        ? `activation after start`
        : `activation offset ${val < 10 ? "0" : ""}${val}s`;
    mqtt_publish("reset", "/ers/timer");
  });

  byName("playing_time").addEventListener("input", (e) => {
    let val = e.srcElement.value;
    byId("time-set-label").innerText = `game duration ${
      val < 10 ? "0" : ""
    }${val}m`;
    // mqtt_publish(val, "/ers/timer/period");
    // mqtt_publish(val, "/er/timer/period");
  });

  byName("back_vol").addEventListener("input", (e) => {
    let val = e.srcElement.value;
    byId("back-vol-label").innerText = `background sound vol ${
      val < 10 ? "0" : ""
    }${val}`;
    mqtt_publish(val, "/er/mc2/vol/set");
  });

  byName("main_vol").addEventListener("input", (e) => {
    let val = e.srcElement.value;
    byId("activ-vol-label").innerText = `active sound vol ${
      val < 10 ? "0" : ""
    }${val}`;

    mqtt_publish(val, "/er/mc1/vol/set");
  });

  byName("selected_language").addEventListener("change", (e) => {});

  // byId("btnReport").addEventListener("click", (e) => {
  //   e.preventDefault();
  //   fetch("/report", {
  //     headers: {
  //       Accept: "application/json",
  //       "X-Requested-With": "XMLHttpRequest",
  //     },
  //   })
  //     .then((response) => {
  //       return response.json();
  //     })
  //     .then((data) => {
  //       console.log(data);
  //     });
  // });

  byId("btnSave").addEventListener("click", (e) => {
    e.preventDefault();
    // mqtt_publish("reset", "/er/async");
    mqtt_publish("", "/er/async/reset");
    // setTimeout(() => {
    console.log("TIME OUT");
    mqtt_publish("reset", "/ers/timer");
    // }, 1000);

    mqtt_publish("reset", "/erp/auto/hint");
    i = document.createElement("input");
    i.hidden = true;
    i.name = "rid-count";
    i.value = len(c) - 1;
    byId("main-form").action = "/config/save";
    byId("main-form").appendChild(i);
    byId("main-form").submit();
  });

  show_all();
  show_selected("selected_language");
  show_selected("selected_dificult");
});
