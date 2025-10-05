const API = "https://notes-app-3-8hk7.onrender.com/";

// -------------------- LOGIN & REGISTER --------------------
async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const msgEl = document.getElementById("msg");

  if (!username || !password) {
    msgEl.textContent = "Please enter username and password.";
    return;
  }

  try {
    const res = await fetch(`${API}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();

    if (!res.ok) {
      msgEl.textContent = data.message || "Login failed.";
      return;
    }

    localStorage.setItem("token", data.token);
    window.location.href = "/notes-page";
  } catch (err) {
    msgEl.textContent = "Error connecting to server.";
    console.error(err);
  }
}

async function register() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const msgEl = document.getElementById("msg");

  if (!username || !password) {
    msgEl.textContent = "Please enter username and password.";
    return;
  }

  try {
    const res = await fetch(`${API}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();

    if (!res.ok) {
      msgEl.textContent = data.message || "Registration failed.";
      return;
    }

    msgEl.style.color = "green";
    msgEl.textContent = data.message || "User registered successfully!";
  } catch (err) {
    msgEl.textContent = "Error connecting to server.";
    console.error(err);
  }
}

// -------------------- NOTES PAGE --------------------
let currentPage = 1;
let currentCategory = '';
let currentSearch = '';

async function createNote() {
  const titleInput = document.getElementById("title");
  const contentInput = document.getElementById("content");
  const categorySelect = document.getElementById("category");
  const isPinnedCheck = document.getElementById("isPinned");

  const title = titleInput.value.trim();
  const content = contentInput.value.trim();
  const category = categorySelect.value;
  const isPinned = isPinnedCheck.checked;

  if (!title || !content) {
    alert("Title and content cannot be empty.");
    return;
  }

  const res = await fetch(`${API}/notes`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + localStorage.getItem("token"),
    },
    body: JSON.stringify({ title, content, category, pinned: isPinned }),
  });

  const data = await res.json();
  alert(data.message);

  titleInput.value = "";
  contentInput.value = "";
  categorySelect.value = "Work";
  isPinnedCheck.checked = false;

  loadNotes();
}

async function updateNote(id, title, content, category, isPinned) {
  const res = await fetch(`${API}/notes/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + localStorage.getItem("token"),
    },
    body: JSON.stringify({ title, content, category, pinned: isPinned }),
  });
  const data = await res.json();
  alert(data.message);
  loadNotes(currentPage);
}

async function deleteNote(id) {
  const res = await fetch(`${API}/notes/${id}`, {
    method: "DELETE",
    headers: { "Authorization": "Bearer " + localStorage.getItem("token") },
  });
  const data = await res.json();
  alert(data.message);
  loadNotes(currentPage);
}

async function loadNotes(page = 1) {
  currentPage = page;
  const token = localStorage.getItem("token");

  if (!token) {
    logout();
    return;
  }

  const res = await fetch(`${API}/notes`, {
    headers: { "Authorization": "Bearer " + token },
  });

  if (res.status === 401) {
    alert("Session expired. Please login again.");
    logout();
    return;
  }

  const notes = await res.json();
  let filteredNotes = notes;

  if (currentCategory) {
    filteredNotes = filteredNotes.filter(n => n.category === currentCategory);
  }

  if (currentSearch) {
    const searchLower = currentSearch.toLowerCase();
    filteredNotes = filteredNotes.filter(
      n => n.title.toLowerCase().includes(searchLower) || n.content.toLowerCase().includes(searchLower)
    );
  }

  const container = document.getElementById("notesList");
  container.innerHTML = "";

  if (filteredNotes.length === 0) {
    container.innerHTML = "<p>No notes found.</p>";
  } else {
    filteredNotes.forEach((n) => {
      const div = document.createElement("div");
      div.className = "note";
      div.innerHTML = `
        <h3>${n.title}</h3>
        <p>${n.content}</p>
        ${n.summary ? `<p style="font-style:italic; color:#555;">Summary: ${n.summary}</p>` : ''}
        <p>Category: ${n.category} | Pinned: ${n.pinned}</p>
        <button onclick="deleteNote(${n.id})">Delete</button>
      `;
      container.appendChild(div);
    });
  }
}

function setCategoryFilter(category) {
  currentCategory = category;
  loadNotes();
}

function setSearchQuery(query) {
  currentSearch = query;
  loadNotes();
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "/";
}

// -------------------- DOMContentLoaded --------------------
document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;

  if (path === "/" || path.includes("login")) {
    document.getElementById("loginBtn")?.addEventListener("click", login);
    document.getElementById("registerBtn")?.addEventListener("click", register);
  }

  if (path.includes("notes-page")) {
    const token = localStorage.getItem("token");
    if (!token) {
      logout();
      return;
    }

    document.getElementById("logoutBtn")?.addEventListener("click", logout);
    document.getElementById("addBtn")?.addEventListener("click", createNote);
    document.getElementById("filterCat")?.addEventListener("change", (e) => setCategoryFilter(e.target.value));
    document.getElementById("search")?.addEventListener("input", (e) => setSearchQuery(e.target.value));
    document.getElementById("refresh")?.addEventListener("click", () => {
      currentCategory = '';
      currentSearch = '';
      document.getElementById("filterCat").value = '';
      document.getElementById("search").value = '';
      loadNotes();
    });

    loadNotes();
  }
});











// const API = "http://127.0.0.1:5000";

// // -------------------- LOGIN & REGISTER --------------------
// async function login() {
//   const username = document.getElementById("username").value.trim();
//   const password = document.getElementById("password").value.trim();
//   const msgEl = document.getElementById("msg");

//   if (!username || !password) {
//     msgEl.textContent = "Please enter username and password.";
//     return;
//   }

//   try {
//     const res = await fetch(`${API}/login`, {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ username, password })
//     });
//     const data = await res.json();

//     if (!res.ok) {
//       msgEl.textContent = data.message || "Login failed.";
//       return;
//     }

//     localStorage.setItem("token", data.token);
//     // ✅ FIX 1: Redirect to the correct Flask route
//     window.location.href = "/notes-page"; 
//   } catch (err) {
//     msgEl.textContent = "Error connecting to server.";
//     console.error(err);
//   }
// }

// async function register() {
//   const username = document.getElementById("username").value.trim();
//   const password = document.getElementById("password").value.trim();
//   const msgEl = document.getElementById("msg");

//   if (!username || !password) {
//     msgEl.textContent = "Please enter username and password.";
//     return;
//   }

//   try {
//     const res = await fetch(`${API}/register`, {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ username, password })
//     });
//     const data = await res.json();

//     if (!res.ok) {
//       msgEl.textContent = data.message || "Registration failed.";
//       return;
//     }

//     msgEl.style.color = "green";
//     msgEl.textContent = data.message || "User registered successfully!";
//   } catch (err) {
//     msgEl.textContent = "Error connecting to server.";
//     console.error(err);
//   }
// }

// // -------------------- NOTES PAGE --------------------
// let currentPage = 1;
// let currentCategory = '';
// let currentSearch = '';

// async function createNote() {
//   const titleInput = document.getElementById("title");
//   const contentInput = document.getElementById("content");
//   const categorySelect = document.getElementById("category");
//   const isPinnedCheck = document.getElementById("isPinned");

//   const title = titleInput.value.trim();
//   const content = contentInput.value.trim();
//   const category = categorySelect.value;
//   const isPinned = isPinnedCheck.checked;

//   if (!title || !content) {
//     alert("Title and content cannot be empty.");
//     return;
//   }

//   const res = await fetch(`${API}/notes`, {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//       "Authorization": "Bearer " + localStorage.getItem("token"),
//     },
//     body: JSON.stringify({ title, content, category, pinned: isPinned }),
//   });

//   const data = await res.json();
//   alert(data.message);

//   titleInput.value = "";
//   contentInput.value = "";
//   categorySelect.value = "Work";
//   isPinnedCheck.checked = false;

//   loadNotes();
// }

// async function updateNote(id, title, content, category, isPinned) {
//   const res = await fetch(`${API}/notes/${id}`, {
//     method: "PUT",
//     headers: {
//       "Content-Type": "application/json",
//       "Authorization": "Bearer " + localStorage.getItem("token"),
//     },
//     body: JSON.stringify({ title, content, category, pinned: isPinned }),
//   });
//   const data = await res.json();
//   alert(data.message);
//   loadNotes(currentPage);
// }

// async function deleteNote(id) {
//   const res = await fetch(`${API}/notes/${id}`, {
//     method: "DELETE",
//     headers: { "Authorization": "Bearer " + localStorage.getItem("token") },
//   });
//   const data = await res.json();
//   alert(data.message);
//   loadNotes(currentPage);
// }

// async function loadNotes(page = 1) {
//   currentPage = page;
//   const token = localStorage.getItem("token");

//   if (!token) {
//     logout();
//     return;
//   }

//   const res = await fetch(`${API}/notes`, {
//     headers: { "Authorization": "Bearer " + token },
//   });

//   if (res.status === 401) {
//     alert("Session expired. Please login again.");
//     logout();
//     return;
//   }

//   const notes = await res.json();
//   let filteredNotes = notes;

//   if (currentCategory) {
//     filteredNotes = filteredNotes.filter(n => n.category === currentCategory);
//   }

//   if (currentSearch) {
//     const searchLower = currentSearch.toLowerCase();
//     filteredNotes = filteredNotes.filter(
//       n => n.title.toLowerCase().includes(searchLower) || n.content.toLowerCase().includes(searchLower)
//     );
//   }

//   const container = document.getElementById("notesList");
//   container.innerHTML = "";

//   if (filteredNotes.length === 0) {
//     container.innerHTML = "<p>No notes found.</p>";
//   } else {
//     filteredNotes.forEach((n) => {
//       const div = document.createElement("div");
//       div.className = "note";
//       div.innerHTML = `
//         <h3>${n.title}</h3>
//         <p>${n.content}</p>
//         <p>Category: ${n.category} | Pinned: ${n.pinned}</p>
//         <button onclick="deleteNote(${n.id})">Delete</button>
//       `;
//       container.appendChild(div);
//     });
//   }
// }

// function setCategoryFilter(category) {
//   currentCategory = category;
//   loadNotes();
// }

// function setSearchQuery(query) {
//   currentSearch = query;
//   loadNotes();
// }

// function logout() {
//   localStorage.removeItem("token");
//   window.location.href = "/"; // ✅ FIX 2: Redirect to home (login)
// }

// // -------------------- DOMContentLoaded --------------------
// document.addEventListener("DOMContentLoaded", () => {
//   const path = window.location.pathname;

//   // ✅ FIX 3: Use strict path checks
//   if (path === "/" || path.includes("login")) {
//     document.getElementById("loginBtn")?.addEventListener("click", login);
//     document.getElementById("registerBtn")?.addEventListener("click", register);
//   }

//   if (path.includes("notes-page")) {
//     const token = localStorage.getItem("token");
//     if (!token) {
//       logout();
//       return;
//     }

//     document.getElementById("logoutBtn")?.addEventListener("click", logout);
//     document.getElementById("addBtn")?.addEventListener("click", createNote);
//     document.getElementById("filterCat")?.addEventListener("change", (e) => setCategoryFilter(e.target.value));
//     document.getElementById("search")?.addEventListener("input", (e) => setSearchQuery(e.target.value));
//     document.getElementById("refresh")?.addEventListener("click", () => {
//       currentCategory = '';
//       currentSearch = '';
//       document.getElementById("filterCat").value = '';
//       document.getElementById("search").value = '';
//       loadNotes();
//     });

//     loadNotes();
//   }
// });
