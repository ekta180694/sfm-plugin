// A Level 2 project shows SFM's model page: four tabs, Building Model with step cards, Baseline and Studio as in SFM.
// Run: node tests/ui_check.mjs <base url>
import { JSDOM, VirtualConsole } from "jsdom";
const BASE = process.argv[2], vc = new VirtualConsole();
const open = async tab => new JSDOM(await (await fetch(`${BASE}/apps/project?tab=${tab}`)).text(), {url: `${BASE}/apps/project?tab=${tab}`,
  runScripts: "dangerously", virtualConsole: vc, pretendToBeVisual: true,
  beforeParse(w) { w.fetch = (x, o) => fetch(x.startsWith("http") ? x : BASE + x, o); }});
const sleep = ms => new Promise(r => setTimeout(r, ms));
const until = async (f, s = 40) => { for (let i = 0; i < s * 10; i++) { try { if (f()) return true; } catch (e) {} await sleep(100); } return false; };
let fails = 0; const check = (n, ok, x = "") => { fails += !ok; console.log(ok ? "PASS" : "FAIL", n, x); };
let d = (await open("building")).window.document;
const nav = () => [...d.querySelectorAll("#nav a")].map(a => a.textContent.trim()).join("|");
check("SFM's page with four tabs", await until(() => nav() === "Building Model|Baseline|Scenario Studio|Optimize & ROI"), nav());
check("no 'All simulation models' link", !d.querySelector("#nav").textContent.includes("All simulation models"));   // body text would include the inline script
check("a waiting step card with Approve", await until(() => [...d.querySelectorAll("button")].some(b => b.textContent.trim() === "Approve")));
d = (await open("baseline")).window.document;
check("Baseline — Current Status, as in SFM", await until(() => d.body.textContent.includes("Baseline — Current Status")));
d = (await open("studio")).window.document;
check("Scenario Studio sections, as in SFM", await until(() => ["Scenario Impact", "Flow Response", "Compare Scenarios"].every(t => d.body.textContent.includes(t))));
process.exit(fails ? 1 : 0);
