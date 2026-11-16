# Лаборатори 11 — Кодны чанар, аюулгүй байдлын тайлан

Статик шинжилгээ (linter) болон dependency scanning-ийг LMS төслийн backend (Django) ба
frontend (React) хэсэгт хийж, илэрсэн асуудлыг засаж, шалгалтыг CI pipeline-д нэгтгэв.

| | Backend (Django) | Frontend (React + Vite) |
|---|---|---|
| Linter | Pylint 4.1.4 + pylint-django 2.8.0 | ESLint 10 (`@eslint/js` recommended + React Hooks + React Refresh) |
| Тохиргоо | `backend/.pylintrc` | `frontend/eslint.config.js` |
| Dependency scan | pip-audit 2.10.1 | `npm audit` |

## 1. Linter — өмнө / дараа

| | Өмнө | Дараа |
|---|---|---|
| **Pylint** | **95 асуудал**, үнэлгээ **8.06/10** | **0 асуудал**, үнэлгээ **10.00/10** |
| **ESLint** | **2 алдаа** | **0** |

Бүрэн гаралт: `pylint_before.txt`, `pylint_after.txt`, `eslint_before.txt`, `eslint_after.txt`.

### 1.1 Pylint — илэрсэн асуудал ба засвар

| Төрөл | Тоо | Юу байсан | Хэрхэн зассан |
|---|---|---|---|
| `missing-*-docstring` (модуль, класс, функц) | 32 | `apps.py`, `admin.py`, `models.py`, `permissions.py`, `serializers.py`, `views.py`, `settings.py` дахь тайлбаргүй класс, функц | **Кодонд** docstring нэмсэн |
| `missing-function-docstring` (тест) | 31 | `test_...` нэртэй тест функцүүд | **Тохиргоо:** `no-docstring-rgx=^_\|^test_` — тестийн нэр нь шалгаж буй зүйлээ аль хэдийн тайлбарладаг (жишээ нь `test_rejects_empty_email`) |
| `redefined-outer-name` | 12 | pytest fixture `api` нь тест функцийн параметртэй ижил нэртэй | **Кодонд:** Pylint-ийн зөвлөдөг `@pytest.fixture(name="api") def fixture_api()` хэлбэрт шилжүүлсэн |
| `line-too-long` (>100) | 8 | Урт мөрүүд (`views.py`, `serializers.py`, `settings.py`, `models.py`) | **Кодонд** мөрийг хуваасан |
| `arguments-renamed` | 1 | `UserManager.get_by_natural_key(self, email)` — Django-гийн эх аргын параметр нь `username` | **Кодонд** параметрийн нэрийг `username` болгосон (Django түүнийг байрлалаар дууддаг тул ажиллагаа өөрчлөгдөхгүй) |
| `raise-missing-from` | 1 | `views.py`: `except` дотор шинэ алдаа шидэхдээ анхны алдааг холбоогүй | **Кодонд** `raise ... from exc` болгосон — алдааны гинжин мэдээлэл хадгалагдана |
| `abstract-method` | 4 | `RegisterSerializer`, `LoginSerializer` нь `create()/update()`-ийг хэрэгжүүлээгүй | **Inline үл хамаарал** тайлбартай: эдгээр нь зөвхөн оролт шалгадаг serializer, хадгалалтыг `services.py` хийдэг |
| `too-many-ancestors` | 2 | `UserCreationForm`, `User.Role` — Django-гийн гүн удамшилтай классууд | **Тохиргоо:** `max-parents=12` — Django-гийн бүтэц, бидний кодоор өөрчлөх боломжгүй |
| `wildcard-import` гэх мэт | 3 | `settings_test.py`: `from config.settings import *` | **Inline үл хамаарал** тайлбартай: Django-гийн тест тохиргооны стандарт арга |
| `import-outside-toplevel` | 1 | `manage.py` (Django-гийн автоматаар үүсгэсэн файл) | **Inline үл хамаарал** тайлбартай: Django суугаагүй үед ойлгомжтой алдаа харуулах зорилготой |

**Нийт 95:** 54 нь кодонд засагдсан, 33 нь тайлбартай 2 тохиргооны дүрмээр, 8 нь шалтгааныг нь
кодонд бичсэн inline үл хамаарлаар шийдэгдсэн.

### 1.2 ESLint — илэрсэн асуудал ба засвар

| Файл | Алдаа | Хэрхэн зассан |
|---|---|---|
| `vite.config.js` | `'process' is not defined` (`no-undef`) | **Тохиргоо:** `vite.config.js`, `eslint.config.js` нь хөтөч биш Node.js дээр ажилладаг тул тэдгээрт Node-ийн `globals` тохируулсан |
| `src/auth/AuthProvider.jsx` | `react-hooks/set-state-in-effect` | **Inline үл хамаарал** тайлбартай: React баримт бичигт заасан "effect дотор өгөгдөл татах" загвар. `setUser`/`setStatus` нь зөвхөн хүсэлт дууссаны дараа `.then()` дотор (`ignore` хамгаалалттай) дуудагддаг, синхрон биш |

## 2. Dependency scanning — эмзэг байдал

| Хэрэгсэл | Шалгасан | Critical | High | Medium | Low |
|---|---|---|---|---|---|
| `pip-audit` | `requirements.txt` + `requirements-dev.txt` | 0 | 0 | 0 | 0 |
| `npm audit` | `frontend/package-lock.json` (бүх сан, ESLint-ийг оруулаад) | 0 | 0 | 0 | 0 |

Бүрэн гаралт: `pip_audit.txt`, `npm_audit.txt`. Шинээр нэмсэн хэрэгслүүд (Pylint, pip-audit,
ESLint)-ийг суулгасны **өмнө ба дараа** хоёуланд нь шалгасан, мэдэгдэж буй эмзэг байдал илрээгүй.

**Дүгнэлт:** Critical/High эрсдэлтэй сан байхгүй тул шинэчлэх шаардлагагүй. Бүх Python санг
`==` тодорхой хувилбараар, npm санг `package-lock.json`-оор түгжсэн тул шалгасан хувилбар нь
production-д яг ижлээр суулгагдана. Шинэ эмзэг байдал хожим нийтлэгдэж болох тул scan-ийг
тогтмол (жишээ нь sprint бүрд, эсвэл GitHub Dependabot-оор) давтахыг санал болгож байна.

## 3. CI pipeline-д нэгтгэсэн нь

`.github/workflows/ci.yml`-д 2 алхам нэмсэн. Аль нэг linter асуудал олбол job улаан болно.

| Job | Шинэ алхам | Команд |
|---|---|---|
| backend | **Lint (Pylint)** — "Install dependencies"-ийн дараа | `pylint $(git ls-files '*.py' \| grep -v '/migrations/')` |
| frontend | **Lint (ESLint)** — "Install dependencies"-ийн дараа | `npx eslint --max-warnings=0 .` |

Pylint, pylint-django, pip-audit-ийг `backend/requirements-dev.txt`-д, ESLint-ийг
`frontend/package.json`-ийн `devDependencies`-д тодорхой хувилбартай нэмсэн тул CI болон багийн
гишүүн бүрийн компьютер дээр ижил дүрэм ажиллана. Frontend-д `npm run lint` скрипт нэмсэн.

## 4. Ажиллагаа өөрчлөгдөөгүйг баталгаажуулсан нь

Засварууд нь зөвхөн кодын чанарт хамаарах бөгөөд програмын ажиллагааг өөрчлөөгүй:

- Backend: **37/37 тест амжилттай**, coverage 96% (засварын өмнө ба дараа ижил)
- `makemigrations --check`: шинэ migration шаардлагагүй
- Frontend: `npm run build` амжилттай

## 5. Локал дээр давтан шалгах

```bash
# Backend
cd backend
pip install -r requirements-dev.txt
pylint $(git ls-files '*.py' | grep -v '/migrations/')
pip-audit -r requirements.txt -r requirements-dev.txt

# Frontend
cd frontend
npm ci
npm run lint
npm audit
```
