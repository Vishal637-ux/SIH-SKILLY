# SKILLY — Frontend Foundation

SKILLY is an Academia–Industry collaboration platform connecting:
- Students
- Colleges / TPOs
- Teachers / Trainers
- Industry / Companies
- Alumni / Mentors

Platform Focus:
Skill Development → Skill Mapping → Career Roadmap → Learning → Internship / Projects → Mentorship → Placement → Career Growth

---

## 🛠 Technology Stack

- **Framework**: React 18
- **Bundler**: Vite
- **Styling**: Tailwind CSS
- **Routing**: React Router v6
- **HTTP Client**: Axios

---

## 📂 Project Structure

```
SKILLY/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── Footer.jsx
│   │   ├── Button.jsx
│   │   ├── PageContainer.jsx
│   │   └── Loading.jsx
│   ├── hooks/
│   ├── lib/
│   │   └── api.js
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── About.jsx
│   │   ├── Features.jsx
│   │   ├── HowItWorks.jsx
│   │   ├── ForStudents.jsx
│   │   ├── ForColleges.jsx
│   │   ├── ForIndustry.jsx
│   │   ├── Contact.jsx
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Student.jsx
│   │   ├── College.jsx
│   │   ├── Teacher.jsx
│   │   ├── Industry.jsx
│   │   ├── Alumni.jsx
│   │   ├── Skills.jsx
│   │   ├── Internships.jsx
│   │   ├── Portfolio.jsx
│   │   ├── Community.jsx
│   │   ├── Notifications.jsx
│   │   └── AI.jsx
│   ├── routes/
│   │   └── AppRoutes.jsx
│   ├── utils/
│   ├── modules/
│   │   ├── public/
│   │   ├── auth/
│   │   ├── student/
│   │   ├── college/
│   │   ├── teacher/
│   │   ├── industry/
│   │   ├── alumni/
│   │   ├── skills/
│   │   ├── internship-placement/
│   │   ├── portfolio/
│   │   ├── community/
│   │   ├── notifications/
│   │   └── ai/
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── .env.example
├── .env
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Variables
Copy `.env.example` to `.env` if not present:
```bash
cp .env.example .env
```

Default configuration:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. Run Development Server
```bash
npm run dev
```

### 4. Build for Production
```bash
npm run build
```
