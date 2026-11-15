# Frontend — React SPA

**React 19** + **Vite** + **React Router**. Сервертэй зөвхөн `/api/...` REST/JSON-оор харилцана
(Лаборатори 5-ын архитектур).

Доорх коммандуудыг **`frontend/` хавтас дотроос** ажиллуулна. Windows, Linux дээр ижил.

## 1. Шаардлагатай програм

| Програм | Хувилбар | Шалгах комманд |
|---|---|---|
| Node.js | **22.22 эсвэл түүнээс дээш** (24 LTS зөвлөмж) | `node --version` |

Татах: <https://nodejs.org/> (LTS хувилбар). `npm` хамт суулгагдана.

## 2. Ажиллуулах

```bash
npm install     # анх удаа, эсвэл package.json өөрчлөгдсөний дараа
npm run dev
```
<http://localhost:5173> хаягаар нээнэ.

Нүүр хуудас нь Frontend, Backend, өгөгдлийн сангийн төлөвийг харуулна. Backend ✗ гэж гарвал
`backend/README.md`-ийн дагуу Django серверийг **өөр terminal дээр** ажиллуулна
(`python manage.py runserver`).

| Комманд | Юу хийх вэ |
|---|---|
| `npm run dev` | Хөгжүүлэлтийн сервер (код өөрчлөхөд автоматаар шинэчлэгдэнэ) |
| `npm run build` | `dist/` хавтсанд production build хийх |
| `npm run preview` | Build хийсэн хувилбарыг локал ажиллуулж шалгах |

## 3. Бүтэц

```
frontend/
├── index.html
├── vite.config.js        # /api, /media хүсэлтийг Django руу дамжуулах (proxy)
└── src/
    ├── main.jsx          # Апп эхлэх цэг (Router)
    ├── App.jsx           # Хуудасны зам (route)-ууд
    ├── index.css         # Ерөнхий загвар
    ├── api/
    │   ├── client.js     # Backend руу хүсэлт илгээх apiFetch()
    │   └── formErrors.js # API-ийн алдааг формд харуулах formErrors()
    ├── auth/             # Нэвтрэлт: AuthProvider, useAuth(), дүрүүд (roles.js)
    ├── components/       # Олон хуудсанд давтагдах хэсгүүд (Layout, RequireAuth, FormField...)
    └── pages/            # Нэг хуудас = нэг файл
```

## 4. Хэрхэн ажиллах вэ

### Шинэ хуудас нэмэх
1. `src/pages/` дотор файл үүсгэнэ, жишээ нь `LoginPage.jsx`.
2. `src/App.jsx`-д route нэмнэ:
   ```jsx
   <Route path="login" element={<LoginPage />} />
   ```

### Backend руу хүсэлт илгээх
`fetch`-ийг шууд ашиглахгүй. Нэвтрэлт шаарддаг хүсэлтийг `useAuth()`-ийн **`authFetch`**-ээр, нээлттэй
хүсэлтийг (`/health/` г.м.) `src/api/client.js`-ийн `apiFetch`-ээр илгээнэ. Хоёулаа ижил параметртэй.
Зам нь `/api`-ийн дараах хэсэг бөгөөд `/`-ээр төгсөнө (Django-ийн URL-тай ижил).
```js
import { ApiError } from '../api/client.js'
import { useAuth } from '../auth/AuthContext.js'

// компонент дотор:
const { authFetch } = useAuth()
const classes = await authFetch('/classes/')

try {
  await authFetch('/classes/join/', { method: 'POST', body: { code: 'AB12CD' } })
} catch (error) {
  if (error instanceof ApiError && error.status === 404) {
    // error.data — Django-ийн буцаасан алдааны JSON
  }
}
```
- `authFetch` нь JWT access token-ийг (`Authorization: Bearer ...`) өөрөө илгээнэ. Token-ий хугацаа
  дууссан бол refresh token-оор шинэчилж нэг удаа дахин оролдоно; чадахгүй бол хэрэглэгчийг гаргана.
- Token-ууд `localStorage`-д (`lms.auth` түлхүүр) хадгалагдана — хуудсыг дахин ачаалахад нэвтэрсэн хэвээр.
- Формд алдаа харуулах: `formErrors(error)` (`src/api/formErrors.js`) → `{ fields: { email: '...' }, general }`,
  талбарыг `components/FormField.jsx`-ээр (`<FormField label error>`) зурна. Жишээ: `pages/RegisterPage.jsx`.
- Файл илгээхдээ `body`-д `FormData` өгнө (US-14).

### Нэвтрэлт ба дүр (US-01)
```js
const { user, logout } = useAuth()   // user = { id, email, role: 'teacher' | 'student' } эсвэл null
```
Нэвтрэлт шаарддаг хуудсыг `App.jsx`-д `<RequireAuth>`-аар ороож, шаардлагатай бол дүрийг заана:
```jsx
<Route path="teacher/classes" element={<RequireAuth role="teacher"><ClassesPage /></RequireAuth>} />
```
Нэвтрээгүй хэрэглэгчийг `/login` руу, өөр дүртэйг өөрийн самбар (`/teacher`, `/student`) руу шилжүүлнэ.

Хөгжүүлэлтийн үед Vite нь `/api`-ийг `http://127.0.0.1:8000` руу дамжуулдаг тул CORS тохиргоо
шаардлагагүй. Backend өөр хаягт ажиллаж байвал `BACKEND_URL` орчны хувьсагчаар солино.

## 5. Багийн дүрэм

- Компонентын файл, нэр **PascalCase** (`ClassCard.jsx`), нэг файлд нэг гол компонент.
- Хэрэглэгчид харагдах текст монгол хэлээр.
- Шинэ сан нэмэхдээ `npm install <сан>` ажиллуулж, **`package.json` болон `package-lock.json` хоёуланг**
  commit хийнэ.
- `node_modules/`, `dist/`-ийг commit хийхгүй (`.gitignore`-д орсон).
