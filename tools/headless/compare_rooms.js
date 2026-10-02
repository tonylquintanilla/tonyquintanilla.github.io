// compare_rooms.js -- drive one room the same way in two copies of the
// gallery and say whether anything differs: the drawer's rows, the count,
// the handle, and the trail of what is drawn and named as every row's box
// is clicked in turn, then All / none and Home. Use it when a change to
// SHARED chrome must leave the other rooms exactly as they were.
//
// Claude-only tooling (L-405); needs jsdom (see page_harness.js).
//   node tools/headless/compare_rooms.js <before> <after> sun /tmp/payload_sun.json
// prints "sun same: true", or both snapshots.
//
// Written October 2, 2026 with Anthropic's Claude Opus 5.5.
const path=require("path");
async function snap(root, ex, payload) {
  
  
  const h=require("./page_harness.js");
  const w=await h.boot(root,ex,payload);
  const d=w.document;
  const rows=[...d.querySelectorAll("#sun-drawer-list > *")].map(r=>(r.hidden?"H ":"")+r.className+"|"+r.textContent.trim());
  const out={status:d.getElementById("loading-status").textContent, errors:h.errors, rows,
    count:d.getElementById("sun-drawer-count").textContent, handle:d.getElementById("sun-drawer-label").textContent,
    info:d.getElementById("info-panel").textContent.length};
  // exercise: toggle each row's box, all/none, home -- record what the scene would show
  const vis=()=>w.eval("sunGroups.map(g=>g.shown?1:0).join('')");
  const trail=[vis()];
  const rowEls=[...d.querySelectorAll("#sun-drawer-list .sun-row:not(.absent)")];
  for (const r of rowEls) { r.querySelector(".pick").dispatchEvent(new w.MouseEvent("click",{bubbles:true})); await h.done(); trail.push(vis()+":"+w.eval("sunFocusIdx")); }
  d.getElementById("sun-drawer-all").click(); await h.done(); trail.push(vis());
  d.getElementById("sun-drawer-all").click(); await h.done(); trail.push(vis());
  await w.eval("navHome()"); trail.push(vis()+":"+w.eval("sunFocusIdx"));
  out.trail=trail; out.errors2=h.errors.slice();
  return out;
}
(async()=>{
  const [a,b,ex,p]=process.argv.slice(2);
  const A=await snap(a,ex,p), B=await snap(b,ex,p);
  console.log(ex, "same:", JSON.stringify(A)===JSON.stringify(B));
  if (JSON.stringify(A)!==JSON.stringify(B)) { console.log(JSON.stringify(A).slice(0,1500)); console.log(JSON.stringify(B).slice(0,1500)); }
  else console.log(" status", A.status, "| rows", A.rows.length, "| count", A.count, "| errors", A.errors.length, A.errors2.length, "| trail", A.trail.join(" "));
})();
