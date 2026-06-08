# Unicompare FE

Frontend Streamlit untuk membandingkan Perguruan Tinggi Negeri (PTN) di Indonesia. Terintegrasi dengan backend API di `https://unicompare-be.vercel.app/api`.

## Daftar Isi

- [Arsitektur](#arsitektur)
- [Struktur Folder](#struktur-folder)
- [Session & State Management](#session--state-management)
  - [Cookies (Token Persistence)](#cookies-token-persistence)
- [API Integration](#api-integration)
- [Performance Optimization](#performance-optimization)
- [Pages](#pages)
- [Running](#running)

---

## Arsitektur

```
User → Streamlit (Python) → HTTP (requests.Session) → Backend API (Vercel)
```

- **Frontend:** Streamlit single-page app dengan 3 halaman (multipage via `st.navigation`)
- **Backend:** REST API terpisah (bukan monolit). Semua data di-fetch via HTTP.
- **State:** Mengandalkan `st.session_state` untuk token auth dan cache data.
- **HTTP Client:** `requests.Session()` dengan connection pooling + timeout.

### Design Pattern

Project ini pake **Service Layer pattern**:

| Layer | Directory | Tanggung Jawab |
|---|---|---|
| **Pages** | `pages/` | UI, layout, user interaction |
| **Components** | `components/` | Reusable UI blocks (comparison cards, eligible programs) |
| **Services** | `services/` | API calls, business logic, state management helpers |
| **Utils** | `utils/` | Data formatting/transformasi untuk display |

Setiap layer cuma boleh komunikasi dengan layer di bawahnya:
```
Pages → Components → Services → Utils
      └─────────────────→ Services
```

---

## Struktur Folder

```
unicompare-fe/
├── app.py                          # Entry point — multipage navigation
├── run.py                          # Helper untuk `streamlit run app.py`
├── requirements.txt                # streamlit, requests, streamlit-cookies-controller
├── .gitignore
│
├── pages/
│   ├── directory.py                # Browse, Find by Score, Compare Programs
│   ├── account.py                  # Login, Register, Profile
│   └── dashboard.py                # Admin CRUD untuk universities & programs
│
├── components/
│   └── compare.py                  # University comparison cards UI
│
├── services/
│   ├── client.py                   # HTTP client wrapper (Session, timeout, auth)
│   ├── auth.py                     # Login, Register, Get Profile
│   └── universities.py             # Universitas & program CRUD + state helpers
│
├── utils/
│   └── format.py                   # Data formatter untuk tabel
│
└── docs/
    └── bruno_collection/           # API collection untuk Bruno
```

---

## Session & State Management

### `st.session_state` — Session-level cache

Streamlit punya `st.session_state` sebagai object storage per browser session. Ini dipake buat:

#### 1. Auth Token (app.py:5-6)

```python
if "token" not in st.session_state:
    st.session_state.token = st.query_params.get("token") or None
```

- Token dibaca dari query param (pas redirect dari backend) atau diset pas login
- Disimpan di `st.session_state.token` — persist selama session browser
- Bisa di-pass ke query param biar bisa di-share (contoh: `?token=xxx`)

#### 2. Data Cache (services/universities.py)

```python
def get_universities():
    if "universities" not in st.session_state:
        st.session_state.universities = fetch_universities()
    return st.session_state.universities
```

**Kenapa?** — Streamlit rerun tiap kali ada interaksi user (klik button, ganti selectbox, dll). Tanpa session state, `fetch_universities()` bakal manggil API tiap rerun — boros banget.

**Cara kerja:**
| Skenario | API Call |
|---|---|
| Pertama kali load halaman | 1 call (`fetch_universities`) |
| Ganti tab (Browse → Compare → Browse) | 0 call (ambil dari session) |
| Ketik search | 0 call untuk daftar universitas (search pake endpoint terpisah) |
| Refresh page | 0 call (session state masih ada) |

#### 3. Programs Cache (services/universities.py:41-47)

```python
def get_programs(uni_id: str):
    key = f"programs_{uni_id}"
    if key not in st.session_state:
        st.session_state[key] = fetch_programs(uni_id)
    return st.session_state[key]
```

Programs di-cache per university ID. Jadi kalo user milih PTN A, balik ke PTN B, trus milih PTN A lagi, data program PTN A udah ada di session — ga perlu fetch ulang.

#### 4. Admin Refresh

Ada `refresh_universities()` buat admin yang butuh data paling baru setelah mutasi data.

---

### Cookies (Token Persistence)

**Library:** `streamlit-cookies-controller`

Streamlit `st.session_state` cuma bertahan selama session browser (tab). Kalo user tutup tab atau refresh, session state ilang. Biar user tetep login, token disimpan di **browser cookies** pake `streamlit-cookies-controller`.

#### Alur Cookie di `app.py:2-18`

```python
from streamlit_cookies_controller import CookieController

if "cookie_controller" not in st.session_state:
    st.session_state.cookie_controller = CookieController()

controller = st.session_state.cookie_controller
cookie_token = controller.get("token")

if "token" not in st.session_state:
    st.session_state.token = st.query_params.get("token") or cookie_token or None

if st.session_state.token and st.session_state.token != cookie_token:
    controller.set("token", st.session_state.token)
elif st.session_state.token is None and cookie_token is not None:
    controller.remove("token")
```

**Cara kerja:**

```
Login sukses
    │
    ├─► account.py: st.session_state.token = token
    ├─► account.py: st.query_params["token"] = token
    ├─► st.rerun()
    │
    └─► app.py (rerun):
          ├─► Detect token baru di session_state
          ├─► controller.set("token", token)  ← simpan ke cookie
          └─► Cookie browser: token tersimpan

Page refresh / buka tab baru
    │
    ├─► app.py: controller.get("token") → dapet dari cookie
    ├─► st.session_state.token = cookie_token
    └─► User tetep login

Logout
    │
    ├─► account.py: st.session_state.token = None
    ├─► account.py: st.query_params.clear()
    ├─► st.rerun()
    │
    └─► app.py (rerun):
          ├─► Detect token = None + cookie masih ada
          ├─► controller.remove("token")  ← hapus cookie
          └─► User bener-bener logout
```

**Kenapa pake `st.query_params` juga?** — Biar backend bisa redirect user dengan token di URL (contoh: setelah OAuth login). Cookies sebagai fallback kalo ga ada query param.

**Perbandingan penyimpanan token:**

| Metode | Scope | Bertahan refresh? | Bisa di-share lewat URL? |
|---|---|---|---|
| `st.session_state` | Session browser | ✗ | ✗ |
| `st.query_params` | URL | ✗ | ✓ |
| `Cookie` | Browser | ✓ | ✗ |

Ketiganya dipake bareng biar:
1. **Query params** — nerima token dari redirect backend
2. **Session state** — akses cepat selama session
3. **Cookie** — persist login antar session

### Flow Diagram Session State

```
User opens app
    │
    ├─► app.py: cek "token" di session_state
    │     │
    │     └─► Tidak ada? Ambil dari query_params
    │
    ├─► directory.py (Browse tab)
    │     │
    │     ├─► get_universities()
    │     │     ├─► Ada di session? → return
    │     │     └─► Ga ada? → fetch → simpan → return
    │     │
    │     └─► search_universities() — pake @st.cache_data
    │
    ├─► directory.py (Compare tab)
    │     │
    │     ├─► get_universities() — reuse dari session
    │     │
    │     └─► User pilih PTN → get_programs(uni_id)
    │           ├─► Ada di session? → return
    │           └─► Ga ada? → fetch → simpan → return
    │
    └─► account.py (Login)
          ├─► login() → API call → dapet token
          ├─► st.session_state.token = token
          ├─► st.query_params["token"] = token
          └─► st.rerun()
```

---

## API Integration

### HTTP Client (`services/client.py`)

Dulu pake `requests.get/post/put/delete` langsung — setiap call bikin koneksi TCP + TLS handshake baru.

Sekarang pake `requests.Session()`:

```python
import requests

BASE_URL = "https://unicompare-be.vercel.app/api"
TIMEOUT = 15

_session = requests.Session()

def api_get(path, token=None, params=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return _session.get(f"{BASE_URL}{path}", headers=headers, params=params, timeout=TIMEOUT)
```

**Apa bedanya?**

| Aspek | Sebelum (`requests.get`) | Sesudah (`Session()`) |
|---|---|---|
| **Koneksi** | Bikin TCP baru tiap call | Reuse koneksi (HTTP Keep-Alive) |
| **TLS Handshake** | Tiap call | Sekali aja |
| **Timeout** | None (bisa ngehang) | 15 detik |
| **Header default** | Harus set manual tiap call | Bisa set di Session level |
| **Connection pool** | Ga ada | Pool otomatis (default 10) |

### Endpoints

| Method | Endpoint | Auth | Fungsi |
|---|---|---|---|
| POST | `/auth/login` | ✗ | Login user |
| POST | `/auth/register` | ✗ | Register user |
| GET | `/auth/me` | Bearer | Profile user |
| GET | `/universities` | ✗ | Semua universities |
| GET | `/universities/search?q=` | ✗ | Search university by name |
| GET | `/universities/{id}` | ✗ | Programs dalam satu university |
| GET | `/compare?score=` | ✗ | Cari eligible programs by score |
| POST | `/admin/universities` | Bearer | Tambah university |
| PUT | `/admin/universities/{id}` | Bearer | Edit university |
| DELETE | `/admin/universities/{id}` | Bearer | Hapus university |
| PUT | `/admin/universities/{id}/programs` | Bearer | Batch update programs |
| POST | `/admin/universities/{id}/programs` | Bearer | Tambah program |
| PUT | `/admin/universities/{id}/programs/{pid}` | Bearer | Edit program |
| DELETE | `/admin/universities/{id}/programs/{pid}` | Bearer | Hapus program |
| GET | `/admin/users` | Bearer | List users (admin only) |

### Auth Flow

```
Login → POST /auth/login → return access_token
    │
    ├─► st.session_state.token = token
    ├─► st.query_params["token"] = token
    ├─► app.py detect token baru → controller.set("token", token)  ← cookie
    │
    └─► Setiap API call dibawah ini:
          api_get("/auth/me", token=st.session_state.token)
          → header "Authorization: Bearer <token>"
```

### Error Handling Pattern

```python
res = api_get("/path")
if res.status_code == 200:
    return res.json()
return None  # atau []
```

Error handling sederhana — return `None` atau list kosong kalo gagal. UI di page layer yang nge-handle:

```python
data = fetch_something()
if not data:
    st.error("Gagal fetch data")
```

---

## Performance Optimization

### 1. Connection Pooling (`requests.Session()`)
- **Masalah:** Tiap API call bikin koneksi TCP + TLS handshake baru (RTT 2-3x lipat)
- **Solusi:** `Session()` otomatis handle HTTP Keep-Alive, pool ukuran 10 koneksi default
- **Dampak:** Latency turun drastis untuk multiple calls (kayak directory + compare)

### 2. Request Timeout (`timeout=15`)
- **Masalah:** Default `timeout=None` → request bisa ngehang selamanya
- **Solusi:** Timeout 15 detik — kalo backend lambat atau down, app tetep responsif

### 3. Session State Caching
- **Masalah:** Streamlit rerun tiap interaksi → `fetch_universities()` dipanggil tiap kali
- **Solusi:** `get_universities()` & `get_programs()` pake `st.session_state`
- **Dampak:** Setelah data pertama di-fetch, 0 API call untuk rerun berikutnya

### 4. Streamlit `@st.cache_data`
- **Masalah:** `search_universities()` dipanggil tiap user ngetik
- **Solusi:** `@st.cache_data` — Streamlit otomatis nyimpen hasil function berdasarkan input
- **Dampak:** Search yang sama ga perlu fetch ulang (in-memory cache)

### Benchmark (estimasi)

| Skenario | Sebelum | Sesudah |
|---|---|---|
| Buka directory page | ~600ms (TCP + TLS + response) | ~400ms (koneksi reuse + response) |
| Ganti tab Browse → Compare | ~600ms (fetch ulang) | 0ms (session state) |
| Pilih PTN di compare | ~400ms (fetch programs) | ~400ms (first time), 0ms (subsequent) |
| Search "Universitas Indonesia" | ~500ms | ~500ms (first), 0ms (cached) |

---

## Pages

### app.py — Entry Point

```python
import streamlit as st
from streamlit_cookies_controller import CookieController

st.set_page_config(page_title="Unicompare")

if "cookie_controller" not in st.session_state:
    st.session_state.cookie_controller = CookieController()

controller = st.session_state.cookie_controller
cookie_token = controller.get("token")

if "token" not in st.session_state:
    st.session_state.token = st.query_params.get("token") or cookie_token or None

if st.session_state.token and st.session_state.token != cookie_token:
    controller.set("token", st.session_state.token)
elif st.session_state.token is None and cookie_token is not None:
    controller.remove("token")

directory = st.Page("pages/directory.py", title="University Directory")
account = st.Page("pages/account.py", title="My Account")
dashboard = st.Page("pages/dashboard.py", title="Admin Dashboard")
pg = st.navigation([directory, account, dashboard])
pg.run()
```

- Pake `st.Page` + `st.navigation` (multipage app)
- Token diambil dari `st.query_params` (redirect login) → fallback ke cookie (persist session)
- Cookie auto-sync: set pas login, remove pas logout

### pages/directory.py

3 tabs:
1. **Browse** — Search & daftar semua universities dalam tabel
2. **Find by Score** — Input score, cari program yang eligible
3. **Compare Programs** — Pilih 2 PTN + program, bandingkan side-by-side

### pages/account.py

2 tabs (kalo belum login): **Login** & **Register**
Kalo udah login: show profile + logout button.

### pages/dashboard.py

Admin only. CRUD untuk universities & programs.
- **Check:** `token` di session_state → `get_profile(token)` → cek role admin
- **Universities:** Expandable list, edit name, delete
- **Programs:** Inline edit (degree + score), add, delete, bulk save

### components/compare.py

Reusable UI:
- `_render_program_card()` — Card untuk pilih PTN + Program
- `render_comparison_ui()` — 2 column comparison layout
- `render_eligible_programs()` — Expandable list program eligible per university

---

## Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run
streamlit run app.py
# atau
python run.py
```

### Devcontainer

Project include `.devcontainer/devcontainer.json` buat development di VS Code Remote Container.

### API Collection

Folder `docs/bruno_collection/` berisi Bruno API collection — 11 request untuk semua endpoints. Bisa di-import ke [Bruno](https://www.usebruno.com/) buat testing.
