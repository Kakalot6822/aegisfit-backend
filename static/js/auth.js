// Mock login → redirect ไป dashboard
if (!localStorage.getItem("token")) {
  // ถ้ายังไม่มี token → ให้กรอกชื่อแล้ว redirect
  const name = prompt("กรอกชื่อผู้ใช้ (demo):");
  if (!name) location.href = "/";        // กลับหน้าแรก
  localStorage.setItem("token", "demo"); // mock token
  localStorage.setItem("userName", name);
}
document.getElementById("userName").textContent = localStorage.getItem("userName");
document.getElementById("logoutBtn").onclick = () => {
  localStorage.clear();
  location.href = "/";
};
