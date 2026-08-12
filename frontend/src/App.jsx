import React, {useEffect, useState} from "react";
import {request, API} from "./api";

const demo = {
  recruiter: {email:"recruiter@demo.com", password:"demo123"},
  candidate: {email:"candidate@demo.com", password:"demo123"}
};

function App(){
  const [user,setUser]=useState(null), [view,setView]=useState("login"), [error,setError]=useState("");
  async function loadMe(){
    try { const u=await request("/auth/me"); setUser(u); setView("dashboard"); }
    catch { localStorage.removeItem("token"); }
  }
  useEffect(()=>{ if(localStorage.getItem("token")) loadMe(); },[]);
  if(!user) return <Auth onLogin={loadMe} error={error} setError={setError}/>;
  return <div className="app"><header><div className="brand">HireAI <span>ATS</span></div><div className="user">{user.name} · {user.role}<button onClick={()=>{localStorage.clear();setUser(null)}}>Logout</button></div></header>
    <main>{user.role==="recruiter" ? <Recruiter/> : <Candidate/>}</main></div>
}

function Auth({onLogin,error,setError}){
  const [mode,setMode]=useState("login"), [role,setRole]=useState("candidate"), [form,setForm]=useState({name:"",email:"",password:""});
  async function submit(e){
    e.preventDefault(); setError("");
    try{
      if(mode==="register"){
        await request("/auth/register",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({...form,role})});
      }
      const d=await request("/auth/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:form.email,password:form.password})});
      localStorage.setItem("token",d.access_token); await onLogin();
    }catch(x){setError(x.message)}
  }
  async function demoLogin(r){
    try{const d=await request("/auth/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(demo[r])});localStorage.setItem("token",d.access_token);await onLogin()}catch(x){setError(x.message)}
  }
  return <div className="auth"><div className="auth-card"><div className="logo">HireAI</div><h1>AI Recruitment & ATS</h1><p className="muted">Find the right talent faster with resume matching.</p>
    <div className="tabs"><button className={mode==="login"?"active":""} onClick={()=>setMode("login")}>Login</button><button className={mode==="register"?"active":""} onClick={()=>setMode("register")}>Register</button></div>
    <form onSubmit={submit}>{mode==="register"&&<input placeholder="Full name" required value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/>}
      <input type="email" placeholder="Email" required value={form.email} onChange={e=>setForm({...form,email:e.target.value})}/>
      <input type="password" placeholder="Password" required value={form.password} onChange={e=>setForm({...form,password:e.target.value})}/>
      {mode==="register"&&<select value={role} onChange={e=>setRole(e.target.value)}><option value="candidate">Candidate</option><option value="recruiter">Recruiter</option></select>}
      <button className="primary">{mode==="login"?"Login":"Create account"}</button>
    </form>
    <div className="demo"><b>Demo:</b><button onClick={()=>demoLogin("recruiter")}>Recruiter</button><button onClick={()=>demoLogin("candidate")}>Candidate</button></div>
    {error&&<div className="error">{error}</div>}
  </div></div>
}

function Recruiter(){
  const [jobs,setJobs]=useState([]),[apps,setApps]=useState([]),[form,setForm]=useState({title:"",company:"",location:"",description:"",required_skills:""}),[msg,setMsg]=useState("");
  async function refresh(){setJobs(await request("/jobs"));setApps(await request("/recruiter/applications"))}
  useEffect(()=>{refresh()},[]);
  async function create(e){e.preventDefault();try{await request("/jobs",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(form)});setForm({title:"",company:"",location:"",description:"",required_skills:""});setMsg("Job created");refresh()}catch(x){setMsg(x.message)}}
  async function status(id,status){try{await request(`/applications/${id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({status})});refresh()}catch(x){setMsg(x.message)}}
  return <div className="dashboard"><div className="hero"><div><h2>Recruiter Dashboard</h2><p>Manage jobs and discover top candidates.</p></div><div className="stats"><Stat n={jobs.length} t="Jobs"/><Stat n={apps.length} t="Applicants"/><Stat n={apps.filter(a=>a.status==="Shortlisted").length} t="Shortlisted"/></div></div>
    <section className="grid2"><div className="card"><h3>Create a job</h3><form onSubmit={create}>{["title","company","location","required_skills"].map(k=><input key={k} placeholder={k.replace("_"," ")} required value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})}/>)}<textarea placeholder="Job description" required value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/><button className="primary">Publish job</button></form>{msg&&<p className="muted">{msg}</p>}</div>
    <div className="card"><h3>Your jobs</h3>{jobs.map(j=><div className="job" key={j.id}><div><b>{j.title}</b><p>{j.company} · {j.location}</p><small>Skills: {j.required_skills}</small></div><button className="danger" onClick={async()=>{await request(`/jobs/${j.id}`,{method:"DELETE"});refresh()}}>Delete</button></div>)}</div></section>
    <section className="card"><h3>Candidate ranking</h3>{apps.length===0?<p className="muted">No applications yet.</p>:<div className="table">{apps.map(a=><div className="row" key={a.id}><div><b>{a.candidate_name}</b><p>{a.job_title}</p></div><strong className="score">{a.match_score}%</strong><span className="status">{a.status}</span><select value={a.status} onChange={e=>status(a.id,e.target.value)}><option>Applied</option><option>Shortlisted</option><option>Interview</option><option>Rejected</option><option>Hired</option></select></div>)}</div>}</section>
  </div>
}

function Candidate(){
  const [jobs,setJobs]=useState([]),[apps,setApps]=useState([]),[skills,setSkills]=useState([]),[msg,setMsg]=useState("");
  async function refresh(){setJobs(await request("/jobs"));setApps(await request("/applications/mine"))}
  useEffect(()=>{refresh()},[]);
  async function upload(e){const fd=new FormData();fd.append("file",e.target.files[0]);try{const d=await request("/resume/upload",{method:"POST",body:fd});setSkills(d.skills);setMsg("Resume analyzed successfully.");refresh()}catch(x){setMsg(x.message)}}
  async function apply(id){try{await request(`/applications/${id}`,{method:"POST"});setMsg("Application submitted and matched.");refresh()}catch(x){setMsg(x.message)}}
  return <div className="dashboard"><div className="hero"><div><h2>Candidate Dashboard</h2><p>Upload your resume and find matching opportunities.</p></div><label className="upload">Upload Resume<input type="file" accept=".pdf,.docx,.txt" onChange={upload}/></label></div>
    {msg&&<div className="notice">{msg}</div>}<section className="card"><h3>Detected skills</h3>{skills.length?<div className="chips">{skills.map(s=><span key={s}>{s}</span>)}</div>:<p className="muted">Upload a PDF, DOCX, or TXT resume to extract skills.</p>}</section>
    <section className="grid2"><div className="card"><h3>Available jobs</h3>{jobs.map(j=>{const a=apps.find(x=>x.job_id===j.id);return <div className="job" key={j.id}><div><b>{j.title}</b><p>{j.company} · {j.location}</p><small>{j.required_skills}</small></div>{a?<span className="score">{a.match_score}% match</span>:<button className="primary small" onClick={()=>apply(j.id)}>Apply</button>}</div>})}</div>
    <div className="card"><h3>My applications</h3>{apps.length?apps.map(a=><div className="row compact" key={a.id}><div><b>{a.job_title}</b><p>{a.status}</p></div><strong className="score">{a.match_score}%</strong></div>):<p className="muted">No applications yet.</p>}</div></section>
  </div>
}

function Stat({n,t}){return <div className="stat"><b>{n}</b><span>{t}</span></div>}
export default App;
