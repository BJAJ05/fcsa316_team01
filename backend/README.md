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
pytest
```
`.env` байгаа бол тест PostgreSQL дээр, байхгүй бол (жишээ нь CI дээр) SQLite дээр ажиллана
(`config/settings_test.py`).

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
├── requirements-dev.txt   # + тестийн сангууд
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

## 6. Багийн дүрэм

- **Хэрэглэгчийн model:** `accounts.User` (имэйлээр нэвтэрдэг, `username` байхгүй). ForeignKey-д
  `settings.AUTH_USER_MODEL`, код дотор `get_user_model()` ашиглана.
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
