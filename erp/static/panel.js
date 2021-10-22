var riddlesInfo = [];
console.log("js");

document.addEventListener("DOMContentLoaded", (e) => {
  e.preventDefault();

  //START MQTT
  mqtt_connect();

  //SET QUEST BUTTONS
  byId("btnStart").addEventListener(
    "click",
    (e) => {
      e.preventDefault();
      console.log("start");
      mqtt_publish("start", "/er/cmd");
      mqtt_publish("start", "/ers/timer");
      // mqtt_publish("", "/ers/timer");
      mqtt_publish("", "/er/musicback/play");
      console.log("start");
      fetch("/statistic/start", {
        headers: {
          Accept: "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
      }).then((response) => {
        return response.json();
      });
    },
    false
  );

  byId("btnAddTime").addEventListener(
    "click",
    (e) => {
      e.preventDefault();
      mqtt_publish("add", "/ers/timer");
    },
    false
  );

  byId("btnReset").addEventListener(
    "click",
    (e) => {
      e.preventDefault();
      console.log("reset");
      mqtt_publish("stop", "/er/clients");
      mqtt_publish("reset", "/er/cmd");
      mqtt_publish("002", "/er/music/play");
      mqtt_publish("reset", "/ers/timer");
      fetch("/statistic/reset", {
        headers: {
          Accept: "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
      }).then((response) => {
        return response.json();
      });
    },
    false
  );

  //SET SCROLL UP/DOWN
  document.addEventListener("scroll", () => {
    document.getElementsByTagName(
      "ul"
    )[0].style.background = `rgba(0, 204, 255, ${
      pageYOffset < 200 ? pageYOffset / 200 : 1
    })`;
  });

  //LOAD DATA
  fetch("/data")
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      console.warn("DATA", data);
      Object.values(data.riddles).forEach((element) => {
        let rid = {
          strId: element.strId,
          strName: element.strName,
          strStatus: "Not activated",
          number: element.number,
          erpNum: element.number,
          soundButtons: element.sound_buttons,
          videoButtons: element.video_buttons,
          lastUpdateTS: Date.now(),
        };
        riddlesInfo.push(rid);
      });
    })
    .catch((err) => {
      console.log(err);
    });

  //SET CARDS ANIMATION
  document.querySelectorAll(".card").forEach((e) => {
    e.onclick = () => {
      document.querySelectorAll(".card").forEach((e) => {
        e.children[0].hidden = false;
        e.children[1].hidden = true;
        e.style.background = "";
        e.style.width = "";
        e.style.hight = "";
        e.style.minWidth = "";
      });
      e.children[0].hidden = true;
      e.children[1].hidden = false;
      e.style.width = "30vw";
      e.style.hight = "400px";
    };
  });

  //SET START RESET FINISH BUTTONS
  let btns_act = document.getElementsByClassName("btn-act");
  Array.from(btns_act).forEach((btn) => {
    btn.onclick = () => {
      let [type, name] = event.srcElement.id.split("_");
      let topic = "/er/" + name + "/cmd";
      // console.log("BUT ", type, " ", topic)
      mqtt_publish(type, topic);
    };
  });

  //SET SOUND AND VIDEO BUTTONS
  let btns = document.getElementsByClassName("btn-2");
  Array.from(btns).forEach((btn) => {
    btn.onclick = () => {
      let [type, rid, num] = event.srcElement.id.split("_");
      let numb = `${parseInt(rid) + parseInt(num) - 1}`;
      let strName = numb.length < 3 ? `0${numb}` : `${numb}`;
      // console.log(type, strName);
      if (type == "hint") mqtt_publish(strName, "/er/async/hint/play");
      // if (type == 'video')
      //     mqtt_publish(strName, ***topic***);
    };
  });

  //EVERY 1 SECOND UPDATE CARD STATUS
  setInterval(() => {
    showStatus();
  }, 2000);
});

function showStatus() {
  let all_card = document.querySelectorAll(".card");
  // console.log(all_card)
  // console.log(riddlesInfo)
  let ind_map = {};
  let c = 0;
  for (let e of all_card) {
    ind_map[e.getAttribute("erpname")] = parseInt(e.getAttribute("order")) - 1;
    c += 1;
  }

  // console.log(ind_map);
  riddlesInfo.forEach((e) => {
    // console.log(element.erpNum);

    if (Math.floor((Date.now() - e.lastUpdateTS) / 1000) > 2)
      e.strStatus = "Offline";
    removeClass(all_card[ind_map[e.strId]]);
    addClass(e);
    showStatuss(e);
  });

  function removeClass(e) {
    // console.log('remove: ', e.classList);
    let cls = e.classList.value.split(" ");
    if (cls.includes("card-reset")) e.classList.remove("card-reset");
    if (cls.includes("card-finish")) e.classList.remove("card-finish");
    if (cls.includes("card-start")) e.classList.remove("card-start");
  }

  function addClass(e) {
    // console.log(e.strName);
    // let i = (e.erpNum < 10) ? e.erpNum - 1 : (e.erpNum) / 10 - 1;
    let i = ind_map[e.strId];
    if (e.strStatus == "Activated") {
      all_card[i].classList.add("card-start");
    } else if (e.strStatus == "Finished") {
      all_card[i].classList.add("card-finish");
    } else if (e.strStatus == "Offline") {
      all_card[i].classList.add("card-reset");
    }
    if (e.strStatus == "Not activated") {
    }
  }

  function showOffline(e) {
    // console.log('off');
  }

  function showStatuss(e) {
    // let i = (e.erpNum < 10) ? e.erpNum - 1 : (e.erpNum) / 10 - 1;
    let i = ind_map[e.strId];
    document.querySelectorAll(".rid_status")[i].innerText =
      e.strStatus.toLowerCase();
  }
}

function byId(name) {
  return document.getElementById(name);
}

function btn() {
  let [type, rid, num] = event.srcElement.id.split("_");
  let numb = `${parseInt(rid) + parseInt(num) - 1}`;
  let strName = numb.length < 3 ? `0${numb}` : `${numb}`;
  console.log(strName);
  mqtt_publish(strName, "/er/hint/play");
}

var MQTT_ADDR = "192.168.10.1";
var MQTT_PORT = 8080;
var clientId = "id_" + parseInt(Math.random() * 1000, 10);
var client = new Messaging.Client(MQTT_ADDR, MQTT_PORT, clientId);
var topic = [
  "/er/ping",
  "/er/name",
  "/er/cmd",
  "/er/timer/client/sec",
  "/er/timer/sec",
  "/er/timer/state",
  "/er/riddles/info",
  "/er/music/info",
  "/er/music/soundlist",
  "/er/clients",
  "/game/period",
  "/game/duration",
  "/unixts",
  "/stat/games/count",
  "/er/mc1/lang/set",
];

var options = {
  timeout: 3,
  onSuccess: () => {
    console.log(
      "MQTT: Connected: " + MQTT_ADDR + ":" + MQTT_PORT + ", id: " + clientId
    );
    topic.forEach((e) => {
      mqtt_subscribe(e);
      // console.log("MQTT: Subscribed: " + e);
    });
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
  // console.log("MQTT: Topic: " + message.destinationName + ", Data: " + message.payloadString);
  msgs_check(message.destinationName, message.payloadString);
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

function msgs_check(topicStr, dataStr) {
  if (topicStr == "/er/timer/client/sec") {
    progress(dataStr);
    if (parseInt(dataStr) == 0) {
      fetch("/statistic/timeup", {
        headers: {
          Accept: "application/json",
          "X-Requested-With": "XMLHttpRequest",
        },
      }).then((response) => {
        return response.json();
      });
    }
  } else if (topicStr == "/er/riddles/info") {
    // console.log(dataStr)
    changeRiddleStatus(parseJSON(dataStr));
  }

  function parseJSON(str) {
    var jsonedObj;
    try {
      jsonedObj = JSON.parse(str);
    } catch (e) {
      console.log('Error: JSON ("' + str + '"): ' + e);
      return null;
    }
    return jsonedObj;
  }

  function progress(secLeft) {
    if (navigator.userAgent.indexOf("Chrome") != -1) {
      byId("maintime").hidden = false;
      byId("timer-firefox").hidden = true;
      byId("maintime").dataset.label = formatTime(parseInt(secLeft));
      byId("maintime").style.backgroundPosition = `0 ${(
        (1 - (secLeft % 60) * 0.0166666) * 0.8 +
        0.12
      ).toFixed(2)}em`;
    }

    if (navigator.userAgent.indexOf("Firefox") != -1) {
      byId("timer-firefox").innerText = formatTime(parseInt(secLeft));
      byId("timer-firefox").hidden = false;
    }

    function formatTime(secLeft) {
      let min = Math.floor(secLeft / 60),
        sec = secLeft % 60;
      return `${min < 10 ? "0" : ""}${min}:${sec < 10 ? "0" : ""}${sec}`;
    }
  }

  function changeRiddleStatus(obj) {
    // console.log(obj)
    let riddle = isRiddleExist(obj.strId);
    if (riddle == null) {
    } else {
      riddle.lastUpdateTS = Date.now();
      if (riddle.strStatus != obj.strStatus) {
        riddle.strStatus = obj.strStatus;
        console.log(
          "Riddle: New status: " + obj.strName + ": " + obj.strStatus
        );
      }
    }

    function isRiddleExist(strId) {
      // console.log(riddlesInfo)
      for (var i = 0; i < riddlesInfo.length; i++)
        if (riddlesInfo[i].strId == strId) return riddlesInfo[i];
      return null;
    }
  }
}
