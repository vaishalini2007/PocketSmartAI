
const $ = (s) => document.querySelector(s);
const token = () => localStorage.getItem('pocket_token');

function nav(){
  const n=$('#nav'); if(!n) return;
  n.innerHTML=token()
    ? `<a href="/dashboard">Dashboard</a><a href="/history">History</a><a href="#" onclick="logout();return false">Logout</a>`
    : `<a href="/login">Login</a><a class="btn primary small" href="/register">Get Started</a>`;
}
nav();

async function api(url,opts={}){
  opts.headers=opts.headers||{};
  if(token()) opts.headers.Authorization='Bearer '+token();
  const r=await fetch(url,opts);
  const d=await r.json().catch(()=>({detail:'Invalid server response'}));
  if(!r.ok) throw new Error(d.detail||'Request failed');
  return d;
}

async function logout(){
  await api('/api/logout',{method:'POST'}).catch(()=>{});
  localStorage.removeItem('pocket_token');
  location.href='/';
}

function money(v){return '₹'+Number(v||0).toLocaleString('en-IN');}
function plannerIcon(type){return type==='home'?'🏠':type==='party'?'🎉':'💎';}

function renderResult(d){
  const box=$('#results'); if(!box) return;
  const allocation=Object.entries(d.allocation||{});
  box.innerHTML=`
  <section class="card result-card">
    <div class="result-head">
      <div class="result-title">
        <div class="result-badge">${plannerIcon(d.planner)}</div>
        <div><span class="tag">${d.ai_used?'GEMINI AI':'SMART FALLBACK'}</span><h2>${String(d.planner||'').toUpperCase()} PLAN</h2><p>${escapeHtml(d.summary||'Your plan is ready.')}</p></div>
      </div>
      <div class="total"><strong>${money(d.total_estimate)}</strong><div class="meta">Remaining ${money(d.remaining)}</div></div>
    </div>
    <h3 class="section-title">Budget allocation</h3>
    <div class="grid allocation">${allocation.map(([k,v])=>`<div class="rec"><span class="tag">${escapeHtml(k)}</span><div class="price">${money(v)}</div><div class="meta">Suggested allocation</div></div>`).join('')}</div>
    <h3 class="section-title">Smart recommendations</h3>
    <div class="recommendations">${(d.recommendations||[]).map(x=>`<article class="rec"><span class="tag">${escapeHtml(x.platform||'RECOMMENDATION')}</span><h3>${escapeHtml(x.name||'Suggested item')}</h3><div class="meta">${escapeHtml(x.category||'General')} • Qty ${Number(x.quantity||1)}</div><div class="price">${money(x.subtotal)}</div><p>${escapeHtml(x.reason||'Budget-aware recommendation.')}</p><a href="${safeUrl(x.link)}" target="_blank" rel="noopener noreferrer">Explore on ${escapeHtml(x.platform||'provider')} ↗</a></article>`).join('')}</div>
    <div class="notice">${escapeHtml(d.disclaimer||'Prices and availability are estimates unless connected to an official provider API.')}</div>
  </section>`;
  box.scrollIntoView({behavior:'smooth',block:'start'});
}

function escapeHtml(v){return String(v??'').replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));}
function safeUrl(v){try{const u=new URL(v||'#',location.origin);return ['http:','https:'].includes(u.protocol)?u.href:'#'}catch{return '#'}}
function setLoading(box, label){if(box) box.innerHTML=`<section class="card loading"><span class="spinner"></span>${label}</section>`}

async function planner(formId,type){
  const f=$(formId); if(!f) return;
  f.addEventListener('submit',async e=>{
    e.preventDefault();
    if(!token()){location.href='/login';return}
    const box=$('#results');
    setLoading(box,'Creating your smart plan...');
    const fd=new FormData(f); let body; let opts={method:'POST'};
    if(type==='jewelry'){
      body=fd; opts.body=body;
    }else{
      body=Object.fromEntries(fd.entries());
      if(type==='home') body={...body,budget:Number(body.budget),rooms:body.rooms.split(',').map(x=>x.trim()).filter(Boolean),items:{}};
      else body={...body,budget:Number(body.budget),guests:Number(body.guests)};
      opts.headers={'Content-Type':'application/json'}; opts.body=JSON.stringify(body);
    }
    try{renderResult(await api('/api/generate-'+type,opts));}
    catch(err){box.innerHTML=`<section class="card error">${escapeHtml(err.message)}</section>`;}
  });
}
planner('#homeForm','home'); planner('#partyForm','party'); planner('#jewelryForm','jewelry');

function authForm(id,mode){
  const f=$(id); if(!f) return;
  f.addEventListener('submit',async e=>{
    e.preventDefault(); const msg=$('#msg');
    if(msg) msg.textContent='';
    try{
      const body=Object.fromEntries(new FormData(f).entries());
      const d=await api('/api/'+mode,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
      localStorage.setItem('pocket_token',d.access_token); location.href='/dashboard';
    }catch(err){if(msg){msg.textContent=err.message;msg.className='error'}}
  });
}
authForm('#loginForm','login'); authForm('#registerForm','register');

async function dashboard(){
  if(!$('#welcome')) return;
  try{
    const s=await api('/api/session-info');
    $('#welcome').textContent=`Welcome, ${s.user.name}. Your saved plans appear below.`;
    const h=await api('/api/history');
    $('#recent').innerHTML=h.length?h.slice(0,5).map(x=>`<div class="history-item"><div class="row"><b>${plannerIcon(x.planner)} ${x.planner.toUpperCase()} PLAN</b><span class="tag">SAVED</span></div><div class="meta">${escapeHtml(x.created_at)}</div></div>`).join(''):'<div class="meta" style="padding-top:18px">No plans yet — choose a planner above to create your first one.</div>';
  }catch(e){location.href='/login'}
}
dashboard();

async function history(){
  if(!$('#historyList')) return;
  try{
    const h=await api('/api/history');
    $('#historyList').innerHTML=h.length?h.map(x=>{const r=JSON.parse(x.result_json);return `<div class="history-item"><div class="row"><b>${plannerIcon(x.planner)} ${x.planner.toUpperCase()} PLAN</b><span>${money(r.total_estimate)}</span></div><div class="meta">${escapeHtml(x.created_at)} • ${r.ai_used?'Gemini AI':'Smart fallback'}</div><p>${escapeHtml(r.summary||'Saved recommendation plan.')}</p></div>`}).join(''):'<div class="meta">No saved recommendations yet.</div>';
  }catch(e){$('#historyList').innerHTML=`<span class="error">${escapeHtml(e.message)}</span>`}
}
history();
