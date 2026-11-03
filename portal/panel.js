// NOQopen control page. Served by the device itself on the home network (noqopen_portal, panel: true) and driven by
// the stock ESPHome web server API: /events (server-sent state of every entity) and POST /<domain>/<name>/<action>.
// Home Assistant can be connected at the same time; both act on the same entities, so changes show up here at once.
// Generic: lights become light cards, everything else is grouped by the firmware's web_server sorting groups.
(function () {
  "use strict";
  var T = {
    tr: {
      kicker: "Cihazın kendi sayfası",
      lede: "Uygulama, hesap ya da bulut gerekmez; bu sayfa doğrudan cihazdan açılır. Telefonunun ana ekranına ekleyebilirsin.",
      connecting: "Cihaza bağlanılıyor…",
      lost: "Bağlantı koptu, yeniden deneniyor…",
      failed: "Gönderilemedi, yeniden dene.",
      haOn: "Home Assistant'a da bağlı",
      haOff: "Home Assistant'sız çalışıyor",
      brightness: "Parlaklık",
      effect: "Efekt",
      group: "Ayarlar",
      tzClock: "Cihaz saati {t}",
      tzNoClock: "Saat henüz alınamadı; internet bağlantısı gelince alınır.",
      tzUse: "Bu telefonun saat dilimini kullan: {z}",
      sure: "Emin misin?",
      cancel: "Vazgeç",
      restarting: "Yeniden başlıyor…",
      resetting: "Sıfırlanıyor. Cihaz kurulum ağını yeniden açar.",
      version: "Yazılım {v}",
      foot: "NOQopen · açık kaynak"
    },
    en: {
      kicker: "Running on the device",
      lede: "No app, account or cloud: this page comes straight from the device. Add it to your phone's home screen.",
      connecting: "Connecting to the device…",
      lost: "Connection lost, retrying…",
      failed: "Could not send, try again.",
      haOn: "Also connected to Home Assistant",
      haOff: "Running without Home Assistant",
      brightness: "Brightness",
      effect: "Effect",
      group: "Settings",
      tzClock: "Device clock {t}",
      tzNoClock: "No clock yet; the device gets it once it can reach the internet.",
      tzUse: "Use this phone's time zone: {z}",
      sure: "Are you sure?",
      cancel: "Cancel",
      restarting: "Restarting…",
      resetting: "Resetting. The device opens its setup network again.",
      version: "Firmware {v}",
      foot: "NOQopen · open source"
    }
  };
  // Names, options and effects as the firmware spells them; anything missing is shown as is.
  var N = {
    tr: {
      "Warm white": "Sıcak beyaz", "Schedule": "Zamanlama", "Schedule start": "Açılış", "Schedule end": "Kapanış",
      "Fade in": "Yükseliş süresi", "Time zone": "Saat dilimi", "Power on": "Elektrik gelince", "Device": "Cihaz",
      "Wi-Fi signal": "Wi-Fi sinyali", "Restart": "Yeniden başlat", "Factory reset": "Fabrika ayarlarına dön",
      "None": "Efekt yok", "Candle": "Mum", "Fireplace": "Şömine", "Breathe": "Nefes", "Flicker": "Titreşim", "Cloud": "Bulut",
      "Last scene": "Son sahneyle yan", "Previous state": "Kesintiden önceki gibi", "Off": "Kapalı kal", "min": "dk"
    },
    en: {
      "Schedule": "Daily schedule", "Schedule start": "On at", "Schedule end": "Off at", "None": "No effect",
      "Last scene": "Light up with the last scene", "Previous state": "As before the power cut", "Off": "Stay off",
      "Factory reset": "Reset to factory settings"
    }
  };
  var HELP = {
    tr: {
      "Schedule": "Her gün açılışta son sahne yavaşça yükselir, kapanışta söner. Işık o saatte açıksa dokunmaz.",
      "Power on": "Duvar anahtarıyla açınca ya da kesintiden sonra elektrik gelince.",
      "Factory reset": "Wi-Fi ve bütün ayarlar silinir."
    },
    en: {
      "Schedule": "Every day the last scene rises slowly at the on time and fades out at the off time. If the light is already on, it is left alone.",
      "Power on": "When a wall switch turns it on, or power comes back after a cut.",
      "Factory reset": "Wi-Fi and all settings are erased."
    }
  };
  // Labels for one entity where its name alone would repeat the card title.
  var BY_ID = {
    tr: { "switch/Schedule": "Her gün otomatik" },
    en: { "switch/Schedule": "Every day" }
  };
  var TONE = { "Amber": "var(--np-tone-amber)", "Warm white": "var(--np-tone-warm)" };
  var SPECIAL = { "binary_sensor/Home Assistant": 1, "text_sensor/Local time": 1 };

  var lang = (navigator.language || "en").toLowerCase().indexOf("tr") === 0 ? "tr" : "en";
  try { var saved = localStorage.getItem("np-lang"); if (saved === "tr" || saved === "en") lang = saved; } catch (x) { /* private mode */ }

  var E = {}, order = [], groups = {}, built = {}, cards = {}, hold = {};
  var info = { title: "", version: "" }, es = null, seen = 0, ready = false, queued = false, flash = 0, gone = false;

  function $(id) { return document.getElementById(id); }
  function t(k, v) {
    var s = T[lang][k];
    for (var key in (v || {})) s = s.split("{" + key + "}").join(v[key]);
    return s;
  }
  function L(name) { return N[lang][name] || name; }
  function label(e) { return BY_ID[lang][e.id] || L(e.name); }
  function help(name) { return HELP[lang][name] || ""; }
  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html) n.innerHTML = html;
    return n;
  }
  function esc(v) {
    return String(v).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c];
    });
  }
  function held(id) {
    var left = (hold[id] || 0) - Date.now();
    if (left <= 0) return false;
    clearTimeout(hold[id + "#"]);
    hold[id + "#"] = setTimeout(function () { update(id, true); }, left + 50);
    return true;
  }
  function touch(id) { hold[id] = Date.now() + 1500; }

  function send(e, action, params) {
    var q = [];
    for (var k in (params || {})) q.push(k + "=" + encodeURIComponent(params[k]));
    var url = "/" + e.domain + "/" + encodeURIComponent(e.name) + "/" + action + (q.length ? "?" + q.join("&") : "");
    return fetch(url, { method: "POST", cache: "no-store" }).then(function (r) {
      if (!r.ok) throw new Error(r.status);
    }).catch(function () { status(t("failed"), 4000); });
  }

  function status(text, ms) {
    $("status").textContent = text || "";
    clearTimeout(flash);
    if (ms) flash = setTimeout(function () { status(ready ? "" : t("connecting")); }, ms);
  }

  // ---- controls -------------------------------------------------------------------------------------------------

  function toggle(label) {
    var b = el("button", "np-switch");
    b.type = "button";
    b.setAttribute("role", "switch");
    b.setAttribute("aria-label", label);
    return b;
  }
  function range(min, max, step) {
    var r = el("input", "np-range");
    r.type = "range"; r.min = min; r.max = max; r.step = step;
    return r;
  }
  function setRange(r, v, min, max) {
    r.value = v;
    r.style.setProperty("--np-fill", ((v - min) / ((max - min) || 1) * 100) + "%");
  }
  function throttle(fn, ms) {
    var last = 0, timer = 0, args = null;
    return function () {
      args = arguments;
      var wait = ms - (Date.now() - last);
      clearTimeout(timer);
      if (wait <= 0) { last = Date.now(); fn.apply(null, args); }
      else timer = setTimeout(function () { last = Date.now(); fn.apply(null, args); }, wait);
    };
  }

  function lightCard(e) {
    var card = el("section", "np-card np-light");
    card.style.setProperty("--np-tone", TONE[e.name] || "var(--np-tone-default)");
    var head = el("div", "np-bar");
    var name = el("div", "np-light-name", "<span class=\"np-glow\" aria-hidden=\"true\"></span><h2 class=\"np-h\">" + esc(L(e.name)) + "</h2>");
    var sw = toggle(L(e.name));
    head.appendChild(name); head.appendChild(sw); card.appendChild(head);

    var f1 = el("div", "np-field");
    var bar = el("div", "np-bar", "<span class=\"np-label\">" + t("brightness") + "</span>");
    var val = el("span", "np-small np-val");
    bar.appendChild(val); f1.appendChild(bar);
    var r = range(1, 100, 1);
    r.setAttribute("aria-label", L(e.name) + " · " + t("brightness"));
    f1.appendChild(r); card.appendChild(f1);

    var fx = el("div", "np-field");
    var pills = el("div", "np-pills");
    pills.setAttribute("role", "group");
    pills.setAttribute("aria-label", t("effect"));
    fx.appendChild(el("span", "np-label", t("effect")));
    fx.appendChild(pills);
    var effects = e.effects || [];
    for (var i = 0; i < effects.length; i++) {
      var p = el("button", "np-pill", esc(L(effects[i])));
      p.type = "button";
      p.setAttribute("data-fx", effects[i]);
      pills.appendChild(p);
    }
    if (effects.length > 1) card.appendChild(fx);

    var sendLevel = throttle(function (pct) { send(e, "turn_on", { brightness: Math.round(pct * 2.55) }); }, 350);
    sw.addEventListener("click", function () {
      var on = E[e.id].state !== "ON";
      E[e.id].state = on ? "ON" : "OFF";
      update(e.id);
      send(e, on ? "turn_on" : "turn_off");
    });
    r.addEventListener("input", function () {
      touch(e.id);
      var pct = +r.value;
      E[e.id].state = "ON";
      E[e.id].brightness = Math.round(pct * 2.55);
      update(e.id, true);
      sendLevel(pct);
    });
    r.addEventListener("change", function () { touch(e.id); });
    pills.addEventListener("click", function (ev) {
      var b = ev.target.closest ? ev.target.closest("[data-fx]") : null;
      if (!b) return;
      var name = b.getAttribute("data-fx");
      E[e.id].effect = name; E[e.id].state = "ON";
      update(e.id);
      send(e, "turn_on", { effect: name });
    });

    return {
      el: card,
      set: function (s, quiet) {
        var on = s.state === "ON", pct = Math.max(1, Math.round((s.brightness || 0) / 2.55));
        card.setAttribute("data-on", on ? "true" : "false");
        card.style.setProperty("--np-level", on ? String(0.35 + 0.65 * pct / 100) : "0");
        sw.setAttribute("aria-checked", on ? "true" : "false");
        val.textContent = on ? pct + "%" : "";
        if (!quiet || !held(e.id)) setRange(r, pct, 1, 100);
        else r.style.setProperty("--np-fill", pct + "%");
        r.setAttribute("aria-valuetext", pct + "%");
        var bs = pills.children;
        for (var j = 0; j < bs.length; j++) bs[j].setAttribute("aria-pressed", bs[j].getAttribute("data-fx") === (s.effect || "None") && on ? "true" : "false");
      }
    };
  }

  function rowShell(e) {
    var row = el("div", "np-set");
    var text = el("div", "np-set-text", "<span class=\"np-set-label\">" + esc(label(e)) + "</span>");
    var h = help(e.name);
    if (h) text.appendChild(el("span", "np-small", esc(h)));
    row.appendChild(text);
    return row;
  }

  function switchRow(e) {
    var row = rowShell(e), sw = toggle(label(e));
    row.appendChild(sw);
    sw.addEventListener("click", function () {
      var on = !E[e.id].value;
      E[e.id].value = on; touch(e.id); update(e.id);
      send(e, on ? "turn_on" : "turn_off");
    });
    return { el: row, set: function (s) { sw.setAttribute("aria-checked", s.value ? "true" : "false"); } };
  }

  function timeRow(e) {
    var row = rowShell(e), input = el("input", "np-time");
    input.type = "time"; input.step = 60; input.setAttribute("aria-label", L(e.name));
    row.appendChild(input);
    input.addEventListener("change", function () {
      if (!/^\d{2}:\d{2}/.test(input.value)) return;
      var v = input.value.slice(0, 5) + ":00";
      E[e.id].value = v; touch(e.id);
      send(e, "set", { value: v });
    });
    input.addEventListener("focus", function () { touch(e.id); });
    return { el: row, set: function (s, quiet) { if (!quiet || !held(e.id)) input.value = String(s.value || "").slice(0, 5); } };
  }

  function numberRow(e) {
    var min = +e.min_value, max = +e.max_value, step = +e.step || 1;
    var f = el("div", "np-field np-set-wide");
    var bar = el("div", "np-bar", "<span class=\"np-set-label\">" + esc(L(e.name)) + "</span>");
    var val = el("span", "np-small np-val");
    bar.appendChild(val); f.appendChild(bar);
    var r = range(min, max, step);
    r.setAttribute("aria-label", L(e.name));
    f.appendChild(r);
    function fmt(v) { return v + (e.uom ? " " + L(e.uom) : ""); }
    r.addEventListener("input", function () { touch(e.id); setRange(r, +r.value, min, max); val.textContent = fmt(r.value); });
    r.addEventListener("change", function () {
      touch(e.id); E[e.id].value = r.value;
      send(e, "set", { value: r.value });
    });
    return {
      el: f,
      set: function (s, quiet) {
        var v = parseFloat(s.value);
        if (isNaN(v)) return;
        if (!quiet || !held(e.id)) { setRange(r, v, min, max); val.textContent = fmt(v); }
      }
    };
  }

  function selectRow(e) {
    var row = rowShell(e);
    row.className = "np-set np-set-wide";
    var list = el("div", "np-list");
    list.setAttribute("role", "radiogroup");
    list.setAttribute("aria-label", L(e.name));
    var opts = e.option || [];
    for (var i = 0; i < opts.length; i++) {
      var b = el("button", "np-row np-opt", "<span class=\"np-row-name\">" + esc(L(opts[i])) + "</span>" +
        "<svg class=\"np-icon np-check\" viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M5 12.5l4.5 4.5L19 7.5\"/></svg>");
      b.type = "button";
      b.setAttribute("role", "radio");
      b.setAttribute("data-opt", opts[i]);
      list.appendChild(b);
    }
    row.appendChild(list);
    list.addEventListener("click", function (ev) {
      var b = ev.target.closest ? ev.target.closest("[data-opt]") : null;
      if (!b) return;
      var o = b.getAttribute("data-opt");
      E[e.id].value = o; touch(e.id); update(e.id);
      send(e, "set", { option: o });
    });
    return {
      el: row,
      set: function (s) {
        var bs = list.children;
        for (var j = 0; j < bs.length; j++) bs[j].setAttribute("aria-checked", bs[j].getAttribute("data-opt") === s.value ? "true" : "false");
      }
    };
  }

  function bars(rssi) {
    var n = rssi > -55 ? 4 : rssi > -67 ? 3 : rssi > -75 ? 2 : 1, out = "";
    for (var i = 0; i < 4; i++) {
      var h = 4 + i * 4;
      out += "<rect" + (i < n ? "" : " class=\"off\"") + " x=\"" + (3 + i * 5) + "\" y=\"" + (20 - h) + "\" width=\"3\" height=\"" + h + "\" rx=\"1\" fill=\"currentColor\" stroke=\"none\"/>";
    }
    return "<svg class=\"np-icon np-bars\" viewBox=\"0 0 24 24\" aria-hidden=\"true\">" + out + "</svg>";
  }

  function valueRow(e) {
    var row = rowShell(e), v = el("span", "np-set-value");
    row.appendChild(v);
    return {
      el: row,
      set: function (s) {
        var num = parseFloat(s.value);
        v.innerHTML = /dBm$/.test(s.state || "") && !isNaN(num) ? bars(num) + "<span>" + esc(s.state) + "</span>" : esc(s.state != null ? s.state : s.value);
      }
    };
  }

  // Time zone: the device keeps "<name>,<std>,<dst>,<start M,w,d,s>,<end M,w,d,s>" (POSIX offsets, seconds west).
  function zoneOf(value) { return String(value || "").split(",")[0]; }
  function phoneZone() {
    var name = "";
    try { name = Intl.DateTimeFormat().resolvedOptions().timeZone || ""; } catch (x) { name = ""; }
    var y = new Date().getFullYear(), start = Date.UTC(y, 0, 1), day = 864e5;
    function off(ms) { return new Date(ms).getTimezoneOffset() * 60; }
    var jan = off(start), jul = off(Date.UTC(y, 6, 1));
    var std = Math.max(jan, jul), dst = Math.min(jan, jul), rules = {};
    if (std !== dst) {
      for (var d = 0; d < 366; d++) {
        var a = start + d * day, b = a + day;
        if (off(a) === off(b)) continue;
        var lo = a, hi = b;
        while (hi - lo > 60000) { var mid = Math.floor((lo + hi) / 2 / 60000) * 60000; if (off(mid) === off(a)) lo = mid; else hi = mid; }
        var before = off(lo), local = new Date(hi - before * 1000);
        var dim = new Date(Date.UTC(local.getUTCFullYear(), local.getUTCMonth() + 1, 0)).getUTCDate();
        var date = local.getUTCDate(), week = date + 7 > dim ? 5 : Math.ceil(date / 7);
        var secs = local.getUTCHours() * 3600 + local.getUTCMinutes() * 60;
        rules[off(hi) === dst ? "start" : "end"] = [local.getUTCMonth() + 1, week, local.getUTCDay(), secs];
      }
    }
    var tail = rules.start && rules.end ? rules.start.concat(rules.end) : [0, 0, 0, 0, 0, 0, 0, 0];
    if (!(rules.start && rules.end)) { std = off(Date.now()); dst = std; }
    if (!name) {
      var east = -std / 60, hh = Math.floor(Math.abs(east) / 60), mm = Math.abs(east) % 60;
      name = "UTC" + (east < 0 ? "-" : "+") + (hh < 10 ? "0" : "") + hh + (mm ? ":" + (mm < 10 ? "0" : "") + mm : "");
    }
    return { name: name, value: [name.replace(/,/g, ""), std, dst].concat(tail).join(",") };
  }

  function zoneRow(e) {
    var row = rowShell(e);
    row.className = "np-set np-set-wide";
    var text = row.firstChild, zone = el("span", "np-set-value"), clock = el("span", "np-small");
    text.appendChild(zone); text.appendChild(clock);
    var use = el("button", "np-link");
    use.type = "button";
    row.appendChild(use);
    var mine = phoneZone();
    use.addEventListener("click", function () {
      E[e.id].value = mine.value; touch(e.id); update(e.id);
      send(e, "set", { value: mine.value });
    });
    return {
      el: row,
      set: function (s) {
        zone.textContent = zoneOf(s.value);
        var c = E["text_sensor/Local time"], now = c && c.value;
        clock.textContent = now ? t("tzClock", { t: now }) : t("tzNoClock");
        use.hidden = s.value === mine.value;
        use.textContent = t("tzUse", { z: mine.name });
      }
    };
  }

  function buttonAction(e, card) {
    var b = el("button", "np-link", esc(L(e.name)));
    b.type = "button";
    b.addEventListener("click", function () {
      var box = card.querySelector(".np-confirm");
      box.hidden = false;
      box.innerHTML = "";
      box.appendChild(el("p", "np-set-label", esc(L(e.name)) + " · " + t("sure")));
      var h = help(e.name);
      if (h) box.appendChild(el("p", "np-small", esc(h)));
      var acts = el("div", "np-actions"), go = el("button", "np-btn", esc(L(e.name))), no = el("button", "np-link", t("cancel"));
      go.type = "button"; no.type = "button";
      acts.appendChild(go); acts.appendChild(no); box.appendChild(acts);
      no.addEventListener("click", function () { box.hidden = true; });
      go.addEventListener("click", function () {
        box.hidden = true;
        send(e, "press").then(function () {
          gone = e.name === "Factory reset";
          status(gone ? t("resetting") : t("restarting"), gone ? 0 : 8000);
        });
      });
      go.focus();
    });
    return b;
  }

  // ---- layout ---------------------------------------------------------------------------------------------------

  function groupCard(name) {
    if (cards[name]) return cards[name];
    var card = el("section", "np-card");
    card.setAttribute("data-w", String(groups[name] != null ? groups[name] : 1e6));
    card.appendChild(el("h2", "np-h", esc(name ? L(name) : t("group"))));
    var rows = el("div", "np-rows"), acts = el("div", "np-actions"), box = el("div", "np-confirm");
    acts.hidden = true; box.hidden = true;
    card.appendChild(rows); card.appendChild(acts); card.appendChild(box);
    cards[name] = card;
    var host = $("groups"), list = [].slice.call(host.children).concat(card);
    list.sort(function (a, b) { return +a.getAttribute("data-w") - +b.getAttribute("data-w"); });
    for (var i = 0; i < list.length; i++) host.appendChild(list[i]);
    return card;
  }

  function place(container, node, weight) {
    node.setAttribute("data-w", String(weight));
    var list = [].slice.call(container.children).concat(node);
    list.sort(function (a, b) { return +a.getAttribute("data-w") - +b.getAttribute("data-w"); });
    for (var i = 0; i < list.length; i++) container.appendChild(list[i]);
  }

  function build(e) {
    if (built[e.id] || !e.domain || SPECIAL[e.id]) return;
    var w = e.sorting_weight != null ? +e.sorting_weight : order.indexOf(e.id);
    if (e.domain === "light") {
      built[e.id] = lightCard(e);
      place($("lights"), built[e.id].el, w);
      return;
    }
    var card = groupCard(e.sorting_group || "");
    if (e.domain === "button") {
      var acts = card.querySelector(".np-actions");
      acts.hidden = false;
      place(acts, buttonAction(e, card), w);
      built[e.id] = { el: null, set: function () {} };
      return;
    }
    var make = e.id === "text/Time zone" ? zoneRow
      : e.domain === "switch" ? switchRow
      : e.domain === "time" ? timeRow
      : e.domain === "number" ? numberRow
      : e.domain === "select" ? selectRow
      : valueRow;
    built[e.id] = make(e);
    place(card.querySelector(".np-rows"), built[e.id].el, w);
  }

  function update(id, quiet) {
    var e = E[id];
    if (e && built[id]) built[id].set(e, quiet);
  }

  function hero() {
    var m = info.title.match(/^(.*?)[ -]([0-9a-f]{6})$/);
    var base = m ? m[1] : info.title;
    $("h-device").textContent = base || "NOQopen";
    document.title = (base || "NOQopen");
    $("chip-host").textContent = location.host || info.title;
    var ha = E["binary_sensor/Home Assistant"];
    $("chip-ha").hidden = !ha;
    if (ha) $("chip-ha").textContent = ha.value ? t("haOn") : t("haOff");
    $("version").textContent = info.version ? t("version", { v: info.version }) : "";
    if (E["text/Time zone"]) update("text/Time zone");
  }

  function render() {
    queued = false;
    for (var i = 0; i < order.length; i++) { build(E[order[i]]); update(order[i], true); }
    hero();
  }
  function later() { if (!queued) { queued = true; requestAnimationFrame(render); } }

  function applyLang() {
    document.documentElement.lang = lang;
    var els = document.querySelectorAll("[data-t]");
    for (var i = 0; i < els.length; i++) els[i].textContent = t(els[i].getAttribute("data-t"));
    var b = document.querySelectorAll("[data-lang]");
    for (var j = 0; j < b.length; j++) b[j].setAttribute("aria-current", b[j].getAttribute("data-lang") === lang ? "true" : "false");
    $("lights").innerHTML = ""; $("groups").innerHTML = "";
    built = {}; cards = {};
    if (!ready) status(t("connecting"));
    render();
  }

  // ---- events ---------------------------------------------------------------------------------------------------

  function connect() {
    if (es) es.close();
    seen = Date.now();
    es = new EventSource("/events");
    es.addEventListener("ping", function (ev) {
      seen = Date.now();
      try {
        var d = JSON.parse(ev.data || "{}");
        if (d.title) info.title = d.title;
        if (d.comment) { var v = String(d.comment).match(/(\d+\.\d+\.\d+)\s*$/); if (v) info.version = v[1]; }
        later();
      } catch (x) { /* keep-alive */ }
    });
    es.addEventListener("sorting_group", function (ev) {
      seen = Date.now();
      try { var g = JSON.parse(ev.data); groups[g.name] = +g.sorting_weight; } catch (x) { /* ignore */ }
    });
    es.addEventListener("state", function (ev) {
      seen = Date.now();
      var d;
      try { d = JSON.parse(ev.data); } catch (x) { return; }
      if (!d || !d.id) return;
      if (!E[d.id]) { E[d.id] = {}; order.push(d.id); }
      for (var k in d) E[d.id][k] = d[k];
      if (!ready) { ready = true; status(""); }
      later();
    });
    es.onerror = function () {
      if (ready && !gone) status(t("lost"));
      es.close(); es = null;
      setTimeout(connect, 3000);
    };
  }
  setInterval(function () { if (es && Date.now() - seen > 25000) { if (!gone) status(t("lost")); connect(); } }, 5000);

  document.addEventListener("click", function (ev) {
    var b = ev.target.closest ? ev.target.closest("[data-lang]") : null;
    if (!b) return;
    lang = b.getAttribute("data-lang");
    try { localStorage.setItem("np-lang", lang); } catch (x) { /* private mode */ }
    applyLang();
  });

  applyLang();
  connect();
})();
