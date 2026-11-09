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
    ├── api/client.js     # Backend руу хүсэлт илгээх apiFetch()
    ├── components/       # Олон хуудсанд давтагдах хэсгүүд (Layout, товч, форм...)
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
`fetch`-ийг шууд биш, `src/api/client.js`-ийн `apiFetch`-ийг ашиглана. Зам нь `/api`-ийн дараах хэсэг
бөгөөд `/`-ээр төгсөнө (Django-ийн URL-тай ижил).
```js
import { ApiError, apiFetch } from '../api/client.js'

const classes = await apiFetch('/classes/', { token })

try {
  await apiFetch('/classes/join/', { method: 'POST', body: { code: 'AB12CD' }, token })
} catch (error) {
  if (error instanceof ApiError && error.status === 404) {
    // error.data — Django-ийн буцаасан алдааны JSON
  }
}
```
- `token` — нэвтэрсний дараа авсан JWT access token (`Authorization: Bearer ...` болж илгээгдэнэ).
  Токеныг хаана хадгалахыг US-01-ийн ажлаар шийднэ.
- Файл илгээхдээ `body`-д `FormData` өгнө (US-14).

Хөгжүүлэлтийн үед Vite нь `/api`-ийг `http://127.0.0.1:8000` руу дамжуулдаг тул CORS тохиргоо
шаардлагагүй. Backend өөр хаягт ажиллаж байвал `BACKEND_URL` орчны хувьсагчаар солино.

## 5. Багийн дүрэм

- Компонентын файл, нэр **PascalCase** (`ClassCard.jsx`), нэг файлд нэг гол компонент.
- Хэрэглэгчид харагдах текст монгол хэлээр.
- Шинэ сан нэмэхдээ `npm install <сан>` ажиллуулж, **`package.json` болон `package-lock.json` хоёуланг**
  commit хийнэ.
- `node_modules/`, `dist/`-ийг commit хийхгүй (`.gitignore`-д орсон).
