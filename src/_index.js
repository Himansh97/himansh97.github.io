
(function(){
"use strict";
var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* ------------------------------------------------------------- reveals
   One observer, unobserve on first hit. A reveal that replays on every
   scroll past is a page that will not settle down and be read. */
var targets = document.querySelectorAll(".entry, .prior, .cell");
if (!("IntersectionObserver" in window) || reduce) {
  for (var i = 0; i < targets.length; i++) targets[i].classList.add("revealed");
} else {
  var io = new IntersectionObserver(function(entries){
    for (var k = 0; k < entries.length; k++) {
      if (!entries[k].isIntersecting) continue;
      entries[k].target.classList.add("revealed");
      io.unobserve(entries[k].target);
    }
  }, { rootMargin: "0px 0px -12% 0px", threshold: 0.12 });
  for (var j = 0; j < targets.length; j++) io.observe(targets[j]);
  /* Anything already on screen at load reveals immediately rather than
     waiting for a scroll that may never come on a short viewport. Done
     synchronously: requestAnimationFrame does not fire at all in a background
     tab, and a portfolio link opened in one would have shown a blank page
     until it was focused. */
  for (var t = 0; t < targets.length; t++) {
    if (targets[t].getBoundingClientRect().top < window.innerHeight * 0.92) {
      targets[t].classList.add("revealed");
      io.unobserve(targets[t]);
    }
  }
  /* Last line of defence. The failure mode of a scroll reveal is content that
     never appears, which is far worse than content that appears without an
     animation — so after a few seconds anything still hidden is simply shown,
     whatever the observer did or did not do. */
  setTimeout(function(){
    for (var v = 0; v < targets.length; v++) targets[v].classList.add("revealed");
  }, 2500);
}

/* ------------------------------------------------ the masthead flow
   The pipeline page's idea at a whisper: postings enter, most die at a
   filter, ten survive and stop. Same log-scaled narrowing, no labels, no
   interaction \u2014 it is a backdrop, and the headline has to stay the loudest
   thing on the page. */
var canvas = document.getElementById("mast");
var header = canvas && canvas.parentNode;
if (!canvas || !header) return;

/* A phone's masthead is all headline. There is no room to be atmospheric in,
   and no reason to spend a GPU on one. */
if (window.innerWidth < 720) { canvas.style.display = "none"; return; }

var gl = null;
try { gl = canvas.getContext("webgl2", { antialias:true, alpha:true, premultipliedAlpha:false }); }
catch(e){ gl = null; }
if (!gl) { canvas.style.display = "none"; return; }

var COUNT = 3800;
/* Real proportions from the run the other page renders: almost everything
   dies at the first filter, and exactly ten come out. */
var DEATHS = [3500, 250, 40, 10];
var U1 = 0.30, U2 = 0.56, U3 = 0.80;
var R0 = 1.00, R1 = 0.723, R2 = 0.506, R3 = 0.250;   // log(survivors)/log(total)

var VERT = [
"#version 300 es",
"precision highp float;",
"in vec4 a_seed;",
"in float a_stage;",
"uniform float u_time;",
"uniform float u_aspect;",
"uniform float u_dpr;",
"uniform float u_band;",
"uniform vec3  u_fit;",   // x scale, x shift, y lift — computed in resize()
"uniform vec3  u_ink;",
"uniform vec3  u_drop;",
"uniform vec3  u_hold;",
"out vec4 v_color;",
"const float XA=-0.18, XB=0.98, CAM=3.0;",
"const float U1=" + U1.toFixed(4) + ", U2=" + U2.toFixed(4) + ", U3=" + U3.toFixed(4) + ";",
"float radiusAt(float u){",
"  float r = " + R0.toFixed(4) + ";",
"  r = mix(r, " + R1.toFixed(4) + ", smoothstep(U1, U1+0.09, u));",
"  r = mix(r, " + R2.toFixed(4) + ", smoothstep(U2, U2+0.09, u));",
"  r = mix(r, " + R3.toFixed(4) + ", smoothstep(U3, U3+0.09, u));",
"  return r * u_band;",
"}",
"void main(){",
"  float u = fract(u_time * 0.062 + a_seed.x);",
"  bool survivor = a_stage > 3.5;",
"  float deathU = a_stage < 1.5 ? U1 : (a_stage < 2.5 ? U2 : (a_stage < 3.5 ? U3 : 9.0));",
"  float uEff = u, hold = 0.0, holdFade = 1.0;",
"  if (survivor) {",
"    float sN = clamp(u / 0.30, 0.0, 1.0);",
"    uEff = 1.0 - pow(1.0 - sN, 2.2);",
"    hold = smoothstep(0.80, 1.0, uEff);",
"    holdFade = 1.0 - smoothstep(0.93, 1.0, u);",
"  }",
"  float dead = max(0.0, u - deathU);",
"  float ang = a_seed.y * 6.2831853 + u_time * 0.04 + a_seed.w * 0.4;",
"  float rad = radiusAt(min(uEff, deathU)) * a_seed.z;",
"  rad += dead * 1.1 * (0.3 + a_seed.w);",
"  float x = XA + uEff * (XB - XA);",
"  if (dead > 0.0) x = XA + deathU * (XB - XA) + dead * 0.22;",
"  float y = sin(ang) * rad - dead * dead * 1.5;",
"  float z = cos(ang) * rad;",
"  float a = smoothstep(0.0, survivor ? 0.010 : 0.035, u);",
"  vec3 col = u_ink;",
"  if (dead > 0.0) {",
"    a *= max(0.0, 1.0 - dead / 0.12);",
"    col = mix(u_drop, u_ink, smoothstep(0.0, 0.05, dead));",
"  } else if (survivor) {",
"    col = mix(u_ink, u_hold, hold);",
"    a *= holdFade * mix(1.0, 1.5, hold);",
"  }",
/* A fixed three-quarter view. There is no orbit because there is nothing to
   inspect \u2014 depth here is only doing the job of making a flat band look like
   it has volume. */
"  vec3 p = vec3(x, y, z);",
"  float cy = cos(0.42), sy = sin(0.42);",
"  p = vec3(p.x*cy + p.z*sy, p.y, -p.x*sy + p.z*cy);",
"  float cx = cos(0.22), sx = sin(0.22);",
"  p = vec3(p.x, p.y*cx - p.z*sx, p.y*sx + p.z*cx);",
"  float w = max(p.z + CAM, 0.06);",
"  float focal = 2.6;",
"  gl_Position = vec4(p.x*focal/(w*u_aspect) * u_fit.x + u_fit.y, p.y*focal/w + u_fit.z, 0.0, 1.0);",
"  gl_PointSize = clamp(2.7 * (survivor ? 2.2 : 1.0) * focal / w, 1.0, 12.0) * u_dpr;",
"  v_color = vec4(col, a * 0.62);",
"}"
].join("\n");

var FRAG = [
"#version 300 es",
"precision highp float;",
"in vec4 v_color;",
"out vec4 outColor;",
"void main(){",
"  vec2 d = gl_PointCoord - vec2(0.5);",
"  float r2 = dot(d, d);",
"  if (r2 > 0.25) discard;",
"  outColor = vec4(v_color.rgb, v_color.a * (1.0 - smoothstep(0.15, 0.25, r2)));",
"}"
].join("\n");

function sh(type, src){
  var x = gl.createShader(type);
  gl.shaderSource(x, src); gl.compileShader(x);
  if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) { console.error(gl.getShaderInfoLog(x)); return null; }
  return x;
}
var vs = sh(gl.VERTEX_SHADER, VERT), fs = sh(gl.FRAGMENT_SHADER, FRAG);
if (!vs || !fs) { canvas.style.display = "none"; return; }
var prog = gl.createProgram();
gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
  console.error("mast: link failed —", gl.getProgramInfoLog(prog));
  canvas.style.display = "none"; return;
}

var seeds = new Float32Array(COUNT * 4), stages = new Float32Array(COUNT), n = 0;
for (var st = 0; st < 4; st++) {
  for (var q = 0; q < DEATHS[st] && n < COUNT; q++) {
    seeds[n*4+0] = Math.random();
    seeds[n*4+1] = Math.random();
    seeds[n*4+2] = Math.sqrt(Math.random());
    seeds[n*4+3] = Math.random();
    stages[n] = st + 1;
    n++;
  }
}
var TOTAL = n;

gl.useProgram(prog);
var vao = gl.createVertexArray();
gl.bindVertexArray(vao);
var b1 = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, b1);
gl.bufferData(gl.ARRAY_BUFFER, seeds, gl.STATIC_DRAW);
var l1 = gl.getAttribLocation(prog, "a_seed");
gl.enableVertexAttribArray(l1); gl.vertexAttribPointer(l1, 4, gl.FLOAT, false, 0, 0);
var b2 = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, b2);
gl.bufferData(gl.ARRAY_BUFFER, stages, gl.STATIC_DRAW);
var l2 = gl.getAttribLocation(prog, "a_stage");
gl.enableVertexAttribArray(l2); gl.vertexAttribPointer(l2, 1, gl.FLOAT, false, 0, 0);

var U = {};
["u_time","u_aspect","u_dpr","u_band","u_fit","u_ink","u_drop","u_hold"].forEach(function(k){
  U[k] = gl.getUniformLocation(prog, k);
});

function rgb(v){
  v = v.trim();
  if (v.charAt(0) === "#") {
    if (v.length === 4) v = "#" + v[1]+v[1] + v[2]+v[2] + v[3]+v[3];
    return [parseInt(v.substr(1,2),16)/255, parseInt(v.substr(3,2),16)/255, parseInt(v.substr(5,2),16)/255];
  }
  var m = v.match(/[\d.]+/g) || [0,0,0];
  return [m[0]/255, m[1]/255, m[2]/255];
}
var theme = {};
function readTheme(){
  var cs = getComputedStyle(document.documentElement);
  theme.ink  = rgb(cs.getPropertyValue("--particle-ink"));
  theme.drop = rgb(cs.getPropertyValue("--particle-drop"));
  theme.hold = rgb(cs.getPropertyValue("--particle-hold"));
}
readTheme();
if (window.matchMedia) {
  var mq = window.matchMedia("(prefers-color-scheme: dark)");
  var onScheme = function(){ readTheme(); if (!running) draw(clock); };
  if (mq.addEventListener) mq.addEventListener("change", onScheme);
  else if (mq.addListener) mq.addListener(onScheme);
}
new MutationObserver(function(){ readTheme(); if (!running) draw(clock); })
  .observe(document.documentElement, { attributes:true, attributeFilter:["data-theme"] });

var W = 1, H = 1, DPR = 1, band = 0.30, fitX = 1, fitS = 0, fitY = 0;
var h1 = header.querySelector("h1");
var XA = -0.18, XB = 0.98;

/* Where the flow sits is measured, not guessed. The first attempt put the
   dense entry cloud behind the headline — the busiest part of the picture in
   the one place it could not be seen and could only do harm — while the open
   right-hand side got ten dots. So the band is placed to start just past the
   headline's own measure and run to the right edge, which holds at any width
   the headline happens to wrap to. */
function ndcOf(x){
  var cy = Math.cos(0.42), sy = Math.sin(0.42);
  var px = x * cy, pz = -x * sy;
  var cx = Math.cos(0.22), sx = Math.sin(0.22);
  pz = pz * cx;                       // y is 0 on the axis
  var w = Math.max(pz + 3.0, 0.06);
  return px * 2.6 / (w * (W / H));
}

function resize(){
  DPR = Math.min(window.devicePixelRatio || 1, 2);
  var r = header.getBoundingClientRect();
  W = Math.max(1, Math.round(r.width));
  H = Math.max(1, Math.round(r.height));
  canvas.width = Math.round(W * DPR);
  canvas.height = Math.round(H * DPR);
  band = 0.30;

  var headW = h1 ? h1.getBoundingClientRect().width : W * 0.45;
  var startPx = Math.min(headW + 56, W * 0.60);
  var ndcStart = (startPx / W) * 2 - 1;
  var a = ndcOf(XA), b = ndcOf(XB);
  fitX = (b - a) !== 0 ? (0.94 - ndcStart) / (b - a) : 1;
  fitS = ndcStart - a * fitX;

  /* Centred on the headline rather than on the header box. Centring on the box
     put the band's lower edge through the first line of the standfirst — the
     header includes the links row underneath, so its middle is well below the
     sentence the band is meant to sit beside. */
  if (h1) {
    var hb = h1.getBoundingClientRect();
    fitY = 1 - 2 * ((hb.top + hb.height / 2) - r.top) / H;
  } else {
    fitY = 0;
  }

  gl.viewport(0, 0, canvas.width, canvas.height);
}

function draw(t){
  gl.clearColor(0, 0, 0, 0);
  gl.clear(gl.COLOR_BUFFER_BIT);
  gl.enable(gl.BLEND);
  gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
  gl.useProgram(prog);
  gl.bindVertexArray(vao);
  gl.uniform1f(U.u_time, t);
  gl.uniform1f(U.u_aspect, W / H);
  gl.uniform1f(U.u_dpr, DPR);
  gl.uniform1f(U.u_band, band);
  gl.uniform3f(U.u_fit, fitX, fitS, fitY);
  gl.uniform3fv(U.u_ink, theme.ink);
  gl.uniform3fv(U.u_drop, theme.drop);
  gl.uniform3fv(U.u_hold, theme.hold);
  gl.drawArrays(gl.POINTS, 0, TOTAL);
}

var clock = reduce ? 5.0 : 0, running = !reduce, last = 0;
function frame(now){
  if (!running) return;
  if (last) clock += Math.min((now - last) / 1000, 0.05);
  last = now;
  draw(clock);
  requestAnimationFrame(frame);
}

resize();
draw(clock);
canvas.classList.add("on");   /* not inside rAF, for the reason above */
if (running) requestAnimationFrame(frame);

/* Scrolled past means stopped. The masthead is decoration for the top of the
   page and there is no reason for it to keep a GPU busy below the fold. */
if ("IntersectionObserver" in window && !reduce) {
  new IntersectionObserver(function(e){
    var vis = e[0].isIntersecting;
    if (!vis) { running = false; }
    else if (!running) { running = true; last = 0; requestAnimationFrame(frame); }
  }, { threshold: 0 }).observe(header);
}

var ro = window.ResizeObserver ? new ResizeObserver(function(){ resize(); draw(clock); }) : null;
if (ro) ro.observe(header);
else window.addEventListener("resize", function(){ resize(); draw(clock); });
})();

})();
