const API = "http://127.0.0.1:8000/api";

export async function request(path, options={}) {
  const token = localStorage.getItem("token");
  const headers = {...(options.headers || {})};
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(API + path, {...options, headers});
  const data = await res.json().catch(()=>({}));
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}
export { API };
