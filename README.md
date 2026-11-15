# Цахим сургалтын нэгдсэн платформ

[![CI](https://github.com/BJAJ05/fcsa316_team01/actions/workflows/ci.yml/badge.svg)](https://github.com/BJAJ05/fcsa316_team01/actions/workflows/ci.yml)

## Багийн гишүүд
- А.Баяржавхлан (Product Owner)
- Б.Тэмүүлэн (Scrum Master)
- Ц.Төгөлдөр (Хөгжүүлэгч)
- Б.Хан-Эрдэнэ (Хөгжүүлэгч)

## Төслийн зорилго
Энэ төслөөр бид Scrum аргачлалыг дагаж, жижиг веб аппликейшн хөгжүүлэх болно.

Багш анги үүсгэж дасгал оруулдаг, сурагч ангийн кодоор нэгдэж дасгал ажиллан дүнгээ шууд хардаг цахим
сургалтын платформ (LMS). Backlog: <https://github.com/users/BJAJ05/projects/1>

## Технологи

| Хэсэг | Технологи | Хавтас |
|---|---|---|
| Клиент | React 19 + Vite + React Router | [`frontend/`](frontend/README.md) |
| Сервер | Python Django 5.2 + Django REST Framework, JWT | [`backend/`](backend/README.md) |
| Өгөгдлийн сан | PostgreSQL | — |

Архитектур: Client-Server + серверийн тал дээр Layered (API → Business → Data Access). Дэлгэрэнгүйг
Лаборатори 5-аас үзнэ үү.

## Эхлүүлэх

1. **Backend:** [`backend/README.md`](backend/README.md)-ийн дагуу PostgreSQL суулгаж, Python venv
   үүсгээд `python manage.py runserver` ажиллуулна → <http://127.0.0.1:8000/api/health/>
2. **Frontend:** өөр terminal дээр [`frontend/README.md`](frontend/README.md)-ийн дагуу
   `npm install`, `npm run dev` → <http://localhost:5173>

Нүүр хуудсанд гурван ✓ (Frontend, Backend, өгөгдлийн сан) гарвал орчин бэлэн болсон.

### Docker-оор ажиллуулах

PostgreSQL, Python, Node суулгалгүйгээр бүх системийг (өгөгдлийн сан + Django + React) контейнерт
ажиллуулна. Docker болон Compose plugin хэрэгтэй (`docker compose version`-оор шалгана).

```bash
docker compose up -d --build   # анх удаа эсвэл код өөрчилсний дараа
```
<http://localhost:8080> нээнэ (нүүр хуудсанд гурван ✓ гарна). Админ хэрэглэгч үүсгэх:
`docker compose exec backend python manage.py createsuperuser` → <http://localhost:8080/admin/>

| Комманд | Юу хийх вэ |
|---|---|
| `docker compose ps` | Контейнеруудын төлөв |
| `docker compose logs -f backend` | Backend-ийн лог |
| `docker compose down` | Зогсоох (өгөгдөл хадгалагдана) |
| `docker compose down -v` | Зогсоож, өгөгдлийн санг устгах |

Энд ашиглагдах нууц үг, түлхүүр нь зөвхөн локал туршилтынх (`docker-compose.yml`). Өөрчлөх бол repo-ийн
үндсэн хавтсанд `.env` файл үүсгэж `DB_PASSWORD=...`, `DJANGO_SECRET_KEY=...` гэж бичнэ (git-д орохгүй).

## Ажлын урсгал (Git)

1. `main`-ийг шинэчилнэ: `git checkout main`, `git pull`
2. User Story бүрд шинэ branch, нэр нь story-ийн дугаар: `git checkout -b us03` (US-03-ийн хувьд)
   (лабораторийн ажил бол `labNN-...`, жишээ нь `lab07-ci`; засвар бол `fix/...`)
3. Жижиг, утга бүхий commit хийнэ. Push хийгээд GitHub дээр `main` руу **Pull Request** нээнэ.
   PR-ын тайлбарт User Story-ийн (эсвэл лабын) дугаарыг бичнэ.
4. **CI** ногоон болмогц PR-ын зохиогч merge хийнэ. Багийн өөр гишүүн code review хийвэл сайн,
   гэхдээ review-г хүлээхгүй.
5. `main` руу шууд push хийхгүй.

CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) нь PR бүр болон `main` руу merge бүрд
backend-ийн migration шалгалт, тестийг (PostgreSQL 16 дээр), frontend-ийн build-ийг ажиллуулна.
CI улаан бол merge хийхгүй — алдааг засаад дахин push хийнэ.

GitHub Projects самбар дээрх картыг ажлын явцын дагуу (In Progress → Review → Done) шилжүүлнэ.

## Лабораторийн ажлуудтай уялдаа

Дараагийн лабораторийн ажлуудыг энэ төсөл дээр хийнэ. Суурийг тэдгээрт бэлэн байхаар тохируулсан
бөгөөд лабын өөрийн ажлыг урьдчилж хийгээгүй:

| Лаб | Сэдэв | Одоо бэлэн байгаа зүйл |
|---|---|---|
| 7 | GitHub Actions CI | **Хийгдсэн:** `.github/workflows/ci.yml` — PR бүр, `main` руу merge бүрд backend (migration шалгалт, PostgreSQL 16 service дээр `pytest`), frontend (`npm ci` → `npm run build`) |
| 8 | Dockerfile, Docker Compose | **Хийгдсэн:** `backend/Dockerfile` (gunicorn, WhiteNoise), `frontend/Dockerfile` (2 шаттай build → nginx), `docker-compose.yml` (db, backend, frontend) — дээрх "Docker-оор ажиллуулах" хэсгийг үзнэ үү |
| 9 | Minikube | `/api/health/` endpoint-ийг liveness/readiness probe болгон ашиглаж болно |
| 10 | Автомат тест | `pytest` + `pytest-django` тохируулагдсан; бизнес логик `services.py`-д тусдаа тул unit тестлэхэд хялбар |
| 11 | Статик шинжилгээ | Linter-ийг санаатайгаар тохируулаагүй — энэ лабаар нэмнэ |
| 13 | Prometheus, Grafana | `/metrics` endpoint-ийг энэ лабаар нэмнэ |
