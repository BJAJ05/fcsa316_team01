# Backend — Django REST API

Python **Django 5.2 (LTS)** + **Django REST Framework** + **PostgreSQL**. JWT нэвтрэлтийг
`djangorestframework-simplejwt` гүйцэтгэнэ. Архитектурын тайлбарыг Лаборатори 5-аас үзнэ үү.

Доорх коммандуудыг **`backend/` хавтас дотроос** ажиллуулна. Windows дээр PowerShell, Linux дээр bash
ашиглана гэж үзсэн.

## 1. Шаардлагатай програмууд

| Програм | Хувилбар | Шалгах комманд |
|---|---|---|
| Python | 3.10 эсвэл түүнээс дээш (3.12+ зөвлөмж) | `python --version` (Linux: `python3 --version`) |
| PostgreSQL | 16 эсвэл түүнээс дээш | `psql --version` |

## 2. PostgreSQL суулгах (нэг удаа)

### Windows
1. <https://www.postgresql.org/download/windows/> хуудаснаас EDB installer-ийг татаж суулгана.
2. Суулгах явцад:
   - **`postgres` хэрэглэгчийн нууц үгийг** тохируулж, сайн тэмдэглэж аваарай (дараа нь хэрэгтэй).
   - Порт: **5432** (өөрчлөхгүй).
   - Төгсгөлд гарах *Stack Builder* шаардлагагүй, алгасна.
3. `psql` коммандыг terminal-аас ажиллуулахын тулд `C:\Program Files\PostgreSQL\<хувилбар>\bin` хавтсыг
   PATH-д нэмнэ (*Edit the system environment variables → Environment Variables → Path → New*).
   Terminal-аа хаагаад дахин нээнэ. Эсвэл Start цэсний **SQL Shell (psql)**-ийг ашиглаж болно.
4. Нэвтрэх: `psql -U postgres` (2-р алхмын нууц үгийг асууна).

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql
sudo systemctl enable --now postgresql
sudo -u postgres psql
```

### Төслийн өгөгдлийн сан, хэрэглэгч үүсгэх
`psql` дотор дараахыг ажиллуулна (`your-password`-ийг өөрийн нууц үгээр солино):
```sql
CREATE USER lms_user WITH PASSWORD 'your-password';
ALTER USER lms_user CREATEDB;
CREATE DATABASE lms_db OWNER lms_user ENCODING 'UTF8' TEMPLATE template0;
\q
```
- `CREATEDB` эрх нь тест ажиллах үед Django түр `test_lms_db` сан үүсгэхэд хэрэгтэй.
- `UTF8` нь монгол текстийг зөв хадгална.

Шалгах: `psql -U lms_user -d lms_db -h localhost` (нууц үг асуугаад нэвтэрвэл болсон).

## 3. Төслийг анх удаа тохируулах

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

**Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Дараа нь `.env` файлыг нээж `DB_PASSWORD`-ийг 2-р алхамд тохируулсан нууц үгээр солино. Тэгээд:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
- <http://127.0.0.1:8000/api/health/> → `{"status": "ok", "database": "ok"}` гарвал бүх зүйл зөв.
- <http://127.0.0.1:8000/admin/> → `createsuperuser`-ээр үүсгэсэн имэйл, нууц үгээр нэвтэрнэ.

> PostgreSQL-ээ суулгаж амжаагүй бол түр хугацаанд `.env` дотор `DB_ENGINE=sqlite` гэж тохируулж
> ажиллуулж болно. Гэхдээ төслийн өгөгдлийн сан нь PostgreSQL тул аль болох хурдан шилжээрэй.

## 4. Өдөр тутмын ажил

Terminal нээх бүрт venv-ээ идэвхжүүлнэ (мөрийн эхэнд `(venv)` гарч ирнэ):
- Windows: `venv\Scripts\Activate.ps1`
- Linux: `source venv/bin/activate`

`main`-аас шинэ өөрчлөлт татсаны дараа:
```bash
pip install -r requirements-dev.txt   # requirements өөрчлөгдсөн бол
python manage.py migrate              # шинэ migration ирсэн бол
python manage.py runserver
```

### Тест ажиллуулах
```bash
pytest                                     # бүх тест
pytest accounts/test_register_user.py -v   # нэг файл, тест бүрийн нэрээр
pytest --cov                               # + coverage: файл бүрийн хувь, тестэд хамрагдаагүй мөрүүд
```
Coverage-д юу тооцогдохыг `pyproject.toml`-д тохируулсан (тест, migration-ийг тооцохгүй).
`.env` байгаа бол тест PostgreSQL дээр, байхгүй бол SQLite дээр ажиллана
(`config/settings_test.py`). CI (GitHub Actions) дээр орчны хувьсагчаар PostgreSQL 16 service-ийг
ашиглана (`.github/workflows/ci.yml`).

### Lint, сангийн аюулгүй байдал
```bash
pylint .                                               # кодын чанар; 10.00/10 байх ёстой (CI шалгана)
pip-audit -r requirements.txt -r requirements-dev.txt  # сангуудад мэдэгдэж буй эмзэг байдал бий эсэх
```
Pylint-ийн дүрэм `.pylintrc`-д (pylint-django plugin, мөрийн урт 100, `migrations/`, `venv/`-ийг
алгасна). Дүрмийг тодорхой мөрөнд үл хэрэгсэх бол `# pylint: disable=<нэр>`-ийн хажууд шалтгааныг
заавал бичнэ.

### Docker image

`Dockerfile` нь gunicorn-оор API-г ажиллуулна (`DEBUG=False`, admin-ий CSS-ийг WhiteNoise өгнө).
Тохиргоо нь `.env` биш, контейнерийн орчны хувьсагчаас уншигдана. `RUN_MIGRATIONS=1` бол контейнер асахдаа
`migrate` хийнэ (`entrypoint.sh`). Ганцаараа SQLite-тэй туршиж үзэх:
```bash
docker build -t lms-backend:1.0 .
docker run --rm -p 8000:8000 -e DJANGO_SECRET_KEY=local-test-insecure-key-0123456789abc \
  -e DB_ENGINE=sqlite -e RUN_MIGRATIONS=1 lms-backend:1.0
```
Бүх системийг хамт ажиллуулах бол үндсэн README-ийн "Docker-оор ажиллуулах" хэсгийг үзнэ үү.

## 5. Бүтэц

```
backend/
├── config/            # Төслийн тохиргоо: settings.py, urls.py, /api/health/
├── accounts/          # Хэрэглэгч, бүртгэл, нэвтрэлт, JWT
├── classrooms/        # Анги, ангийн код, элсэлт, сурагчдын жагсаалт
├── assignments/       # Даалгавар, асуулт, хавсралт файл
├── grading/           # Илгээлт, автомат дүгнэлт, алдаа давтах
├── analytics/         # Сурагчийн ахиц, багшийн тайлан
├── requirements.txt       # Ажиллахад шаардлагатай сангууд
├── requirements-dev.txt   # + тест, lint, pip-audit
├── pyproject.toml         # pytest, coverage-ийн тохиргоо
├── .pylintrc              # Pylint-ийн дүрэм
└── .env.example           # .env-ийн загвар
```

| App | URL prefix | User Story |
|---|---|---|
| `accounts` | `/api/auth/` | US-01 |
| `classrooms` | `/api/classes/` | US-02, US-03, US-04 |
| `assignments` | `/api/assignments/` | US-05, US-06, US-14 |
| `grading` | `/api/submissions/` | US-07, US-08 |
| `analytics` | `/api/analytics/` | US-12, US-13 |

Спринт 1-д ороогүй тэмдэглэл (US-09), AI (US-10, US-11)-д шаардлагатай үед шинэ app нэмнэ:
`python manage.py startapp notes`, дараа нь `config/settings.py`-ийн `INSTALLED_APPS` болон
`config/urls.py`-д бүртгэнэ.

### Давхаргын дүрэм (Лаб 5-ын Layered архитектур)
App бүр ижил 3 давхаргатай:

| Файл | Давхарга | Юу байх вэ |
|---|---|---|
| `views.py` (+ `serializers.py`) | Presentation / API | HTTP хүсэлт хүлээн авах, эрх шалгах, оролт баталгаажуулах |
| `services.py` | Business | Бизнес логик (жишээ нь ангийн код үүсгэх, оноо бодох) |
| `models.py` | Data Access | Django model, өгөгдлийн сан |

View нь өгөгдлийн сан руу шууд хандахгүй, `services.py`-ийн функцийг дуудна. Ингэснээр бизнес логикийг
HTTP-гүйгээр unit тестлэх боломжтой.

### Нэвтрэлтийн API (US-01)

| Хүсэлт | Body | Хариу |
|---|---|---|
| `POST /api/auth/register/` | `{email, password, role}` — `role` нь `teacher` эсвэл `student` | `201 {user, access, refresh}`; имэйл давхардвал `400 {"email": ["Энэ имэйл бүртгэлтэй байна."]}` |
| `POST /api/auth/login/` | `{email, password}` | `200 {user, access, refresh}`; буруу бол `401 {"detail": "Имэйл эсвэл нууц үг буруу байна."}` |
| `POST /api/auth/refresh/` | `{refresh}` | `200 {access}` (access token 60 минут, refresh token 7 хоног хүчинтэй) |
| `GET /api/auth/me/` | — (token шаардана) | `200 {id, email, role}` |

- `user` нь `{id, email, role}`. Access token дотор `role`, `email` claim бий (frontend самбараа сонгоход
  ашиглана); серверийн эрх шалгалт өгөгдлийн сангаас уншдаг.
- Имэйлийг жижиг үсгээр хадгалдаг тул бүртгэл, нэвтрэлтэд том жижиг үсэг ялгахгүй.
- Дүрээр эрх шалгах: `accounts/permissions.py`-ийн `IsTeacher`, `IsStudent`; код дотор
  `request.user.is_teacher`, `request.user.is_student`.
  ```python
  from accounts.permissions import IsTeacher

  class CreateClassView(APIView):
      permission_classes = [IsTeacher]
  ```

### Ангийн API (US-02, US-03, US-04)

Анги бүрийн хариу: `{id, name, subject, code, teacher_email, student_count, created_at}`.

| Хүсэлт | Хэн | Body | Хариу |
|---|---|---|---|
| `GET /api/classes/` | багш, сурагч | — | `200 [анги]` — багшид өөрийн үүсгэсэн, сурагчид элссэн ангиуд (шинэ нь эхэндээ) |
| `POST /api/classes/` | багш | `{name, subject}` — хоёулаа заавал | `201 анги`; код нь 6 тэмдэгт (A–Z, 0–9), давхцахгүй |
| `GET /api/classes/<id>/` | багш, сурагч | — | `200 анги`; өөрийн бус / элсээгүй анги бол `404 {"detail": "Анги олдсонгүй."}` |
| `POST /api/classes/join/` | сурагч | `{code}` | `201 анги`; кодыг жижиг үсэг, хоосон зайтай оруулсан ч хүлээн авна |
| `GET /api/classes/<id>/students/` | багш (эзэн) | — | `200 [{id, email, joined_at}]` — имэйлээр эрэмбэлсэн |
| `DELETE /api/classes/<id>/students/<student_id>/` | багш (эзэн) | — | `204`; элсээгүй сурагч бол `404 {"detail": "Сурагч энэ ангид элсээгүй байна."}` |

`POST /api/classes/join/`-ийн алдаа: байхгүй код → `404 {"detail": "Ангийн код олдсонгүй."}`,
аль хэдийн элссэн → `400 {"code": ["Та энэ ангид аль хэдийн элссэн байна."]}`, хоосон код →
`400 {"code": ["Ангийн кодыг оруулна уу."]}`. Элсэлт `Enrollment` хүснэгтэд хадгалагдана
(`classroom.students`, `user.joined_classes`).

Сурагчдын жагсаалтыг (US-04) зөвхөн тухайн ангийн багш харж, засна: өөр багш → `404`, сурагч → `403`.
Хасагдсан сурагч ангид хандах эрхээ алдана (`GET /api/classes/<id>/` → `404`), гэхдээ ангийн кодоор
дахин элсэж болно. Түүний өмнөх илгээлтүүд хадгалагдана.

### Даалгаврын API (US-05, US-06)

Даалгавар бүрийн хариу: `{id, classroom, title, instructions, due_date, is_open, question_count,
created_at}`.
`due_date` нь ISO 8601, цагийн бүстэй (`"2026-12-01T18:00:00+08:00"`); `is_open` нь дуусах хугацаа
өнгөрөөгүй бол `true`.

| Хүсэлт | Хэн | Body | Хариу |
|---|---|---|---|
| `GET /api/assignments/?classroom=<id>` | багш, сурагч | — | `200 [даалгавар]` — дуусах хугацаагаар эрэмбэлсэн |
| `POST /api/assignments/` | багш (ангийн эзэн) | `{classroom, title, instructions, due_date}` — `instructions` заавал биш | `201 даалгавар` |
| `GET /api/assignments/<id>/` | багш, сурагч | — | `200 даалгавар` + `questions` (доор) |
| `PATCH /api/assignments/<id>/` | багш (эзэн) | `{title?, instructions?, due_date?}` | `200 даалгавар`; ангийг өөрчлөх боломжгүй |
| `DELETE /api/assignments/<id>/` | багш (эзэн) | — | `204` |
| `POST /api/assignments/<id>/questions/` | багш (эзэн) | асуулт (доор) | `201 асуулт`; даалгаврын төгсгөлд нэмэгдэнэ |
| `DELETE /api/assignments/<id>/questions/<question_id>/` | багш (эзэн) | — | `204` |

Алдаа: өөрийн бус / элсээгүй анги → `404 {"detail": "Анги олдсонгүй."}`, өөрийн бус / байхгүй
даалгавар → `404 {"detail": "Даалгавар олдсонгүй."}`, `?classroom=` эсвэл `classroom` дутуу →
`400 {"classroom": ["Ангийг сонгоно уу."]}`, өнгөрсөн огноо (үүсгэх, PATCH) →
`400 {"due_date": ["Дуусах хугацаа ирээдүйд байх ёстой."]}`, нэргүй →
`400 {"title": ["Даалгаврын нэрийг оруулна уу."]}`, хугацаагүй →
`400 {"due_date": ["Дуусах хугацааг оруулна уу."]}`. Сурагч `POST/PATCH/DELETE` хийвэл `403`.

**Асуулт (US-06).** Хоёр загвар:

```json
{"kind": "multiple_choice", "text": "2 + 2 = ?", "points": 2,
 "choices": [{"text": "3", "is_correct": false}, {"text": "4", "is_correct": true}]}
{"kind": "fill_in", "text": "Монголын нийслэл?", "points": 1, "correct_answer": "Улаанбаатар"}
```

`points` заавал биш (анхдагч 1). Олон сонголттойд хоосон сонголтыг хасаад 2–6 сонголт, яг нэг зөв
хариулт байх ёстой. `GET /api/assignments/<id>/`-ийн `questions`: **багшид**
`{id, kind, text, points, position, correct_answer, choices: [{id, text, is_correct}]}`, **сурагчид**
`{id, kind, text, points, choices: [{id, text}]}` — зөв хариулт сурагчид хэзээ ч очихгүй.

Асуултын алдаа (`400`): `{"text": ["Асуултын текстийг оруулна уу."]}`,
`{"points": ["Оноо 1-ээс бага байж болохгүй."]}`, `{"kind": ["Асуултын төрлийг сонгоно уу."]}`,
`{"choices": ["Хамгийн багадаа 2 сонголт оруулна уу."]}` / `["Хамгийн ихдээ 6 сонголт оруулна уу."]` /
`["Зөв хариултыг сонгоно уу."]` / `["Зөвхөн нэг зөв хариулт сонгоно уу."]`,
`{"correct_answer": ["Зөв хариултыг оруулна уу."]}`. Байхгүй асуулт → `404 {"detail": "Асуулт олдсонгүй."}`.
Илгээлт хийгдсэн даалгаврын асуултыг нэмэх, устгах → `400 {"non_field_errors": ["Илгээлт хийгдсэн тул
асуултыг өөрчлөх боломжгүй."]}` (US-07).

### Илгээлтийн API (US-07)

| Хүсэлт | Хэн | Body | Хариу |
|---|---|---|---|
| `POST /api/submissions/` | сурагч (элссэн) | `{assignment, answers}` | `201 илгээлт` — автоматаар дүгнэсэн |
| `GET /api/submissions/<id>/` | сурагч (өөрийн) | — | `200 илгээлт`; бусдынх бол `404 {"detail": "Илгээлт олдсонгүй."}` |

```json
{"assignment": 5, "answers": [{"question": 11, "choice": 31}, {"question": 12, "text": "улаанбаатар"}]}
```

Олон сонголттой асуултад `choice`, нөхөх асуултад `text`. Хариулаагүй асуултыг орхиж болно (буруу гэж
тооцогдоно). Нөхөх хариултыг том жижиг үсэг, илүү зайг үл харгалзан харьцуулна. Илгээлт:
`{id, assignment, assignment_title, classroom, score, max_score, percent, submitted_at, results}`,
`results`: асуулт бүрд `{question, text, kind, your_answer, is_correct, points_awarded, points}`.
**Зөв хариулт хэзээ ч буцахгүй.** Сурагч нэг даалгаврыг нэг л удаа илгээнэ. Даалгаврын хариунд (сурагчид)
`submission: {id, score, max_score, percent} | null` нэмэгдсэн.

Алдаа (`400`): `{"non_field_errors": ["Даалгаврын хугацаа дууссан байна."]}` /
`["Та энэ даалгаврыг аль хэдийн илгээсэн байна."]` / `["Энэ даалгаварт асуулт алга байна."]`,
`{"answers": ["Асуулт энэ даалгаварт хамаарахгүй."]}` / `["Нэг асуултад нэг л хариулт илгээнэ үү."]`.
Элсээгүй ангийн даалгавар → `404 {"detail": "Даалгавар олдсонгүй."}`. Багш → `403`.

Оноо бодох логик `grading/scoring.py`-д (өгөгдлийн сангүй, Лаб 5-ын `check()`, `grade()`), хадгалах нь
`grading/services.py`-д.

### Сурагчийн ахицын API (US-12)

`GET /api/analytics/progress/` — зөвхөн сурагч (багшид `403`). Элссэн анги бүрийн даалгаврын тоо,
илгээсэн тоо, гүйцэтгэлийн хувь, илгээлтийн дундаж хувь болон даалгавар тус бүрийн оноог буцаана.
Илгээгээгүй даалгаврын `percent`, илгээлтгүй ангийн `average_percent` нь `null`; даалгаваргүй ангийн
гүйцэтгэл `0` байна.

## 6. Багийн дүрэм

- **Хэрэглэгчийн model:** `accounts.User` (имэйлээр нэвтэрдэг, `username` байхгүй). ForeignKey-д
  `settings.AUTH_USER_MODEL`, код дотор `from accounts.models import User` ашиглана.
  (`get_user_model()`-ийг VS Code зөвхөн Django-гийн ерөнхий хэрэглэгч гэж таньдаг тул `User.Role`,
  `user.is_teacher` зэрэг дээр алдаа заадаг.)
- **Төрлийн шалгалт (VS Code / Pylance):** `requirements-dev.txt`-ийн `django-stubs`,
  `djangorestframework-stubs` нь Django, DRF-ийн төрлийг editor-т өгнө. VS Code дээр backend-ийн
  `venv`-ийг Python interpreter болгон сонгосон байх ёстой. Алдааг `# type: ignore`-оор нуухгүй, кодыг
  засна.
- **Эрх:** API нь анхдагчаар нэвтэрсэн хэрэглэгч шаарддаг. Бүртгэл, нэвтрэлт зэрэг нээлттэй endpoint-д
  `permission_classes = [AllowAny]` гэж тодорхой бичнэ.
- **URL:** бүх API зам `/`-ээр төгсөнө (`POST /api/auth/register/`).
- **Migration:** model өөрчилсний дараа `python manage.py makemigrations` ажиллуулж, үүссэн migration
  файлыг **заавал commit** хийнэ. Хоёр хүн нэг app-д зэрэг migration үүсгэвэл merge хийсний дараа
  `python manage.py makemigrations --merge` ажиллуулна.
- **Шинэ сан нэмэх:** `pip install <сан>`, дараа нь `requirements.txt`-д хувилбартай нь
  (`нэр==1.2.3`) нэмнэ.
- **Нууц мэдээлэл:** `.env` файлыг хэзээ ч commit хийхгүй. Шинэ тохиргоо нэмбэл `.env.example`-д
  жишээ утгатай нь нэмнэ.

## 7. Түгээмэл асуудал

| Алдаа | Шийдэл |
|---|---|
| PowerShell: `Activate.ps1 cannot be loaded because running scripts is disabled` | Нэг удаа `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` ажиллуулна. |
| Linux: `ensurepip is not available` | `sudo apt install python3-venv` |
| `DJANGO_SECRET_KEY is not set` | `.env.example`-ийг `.env` болгон хуулаагүй байна (3-р алхам). |
| `password authentication failed for user "lms_user"` | `.env` дахь `DB_PASSWORD` нь 2-р алхмын нууц үгтэй таарахгүй байна. |
| `connection refused` / `/api/health/` → `"database": "unavailable"` | PostgreSQL service ажиллаагүй байна. Windows: *Services* → `postgresql-x64-<хувилбар>` → Start. Linux: `sudo systemctl start postgresql` |
| `psql: command not found` / `'psql' is not recognized` | PostgreSQL-ийн `bin` хавтас PATH-д ороогүй байна (2-р алхам). |
| `permission denied to create database` (pytest) | `ALTER USER lms_user CREATEDB;` |
