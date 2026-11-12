# Цахим сургалтын нэгдсэн платформ

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

## Ажлын урсгал (Git)

1. `main`-ийг шинэчилнэ: `git checkout main`, `git pull`
2. User Story бүрд шинэ branch, нэр нь story-ийн дугаар: `git checkout -b us03` (US-03-ийн хувьд)
   (засвар бол `fix/...`, тохиргоо бол `chore/...`)
3. Жижиг, утга бүхий commit хийнэ. Push хийгээд GitHub дээр `main` руу **Pull Request** нээнэ.
   PR-ын тайлбарт User Story-ийн дугаарыг бичнэ.
4. Багийн өөр нэг гишүүн **code review** хийж зөвшөөрсний дараа merge хийнэ.
5. `main` руу шууд push хийхгүй.

GitHub Projects самбар дээрх картыг ажлын явцын дагуу (In Progress → Review → Done) шилжүүлнэ.

## Лабораторийн ажлуудтай уялдаа

Дараагийн лабораторийн ажлуудыг энэ төсөл дээр хийнэ. Суурийг тэдгээрт бэлэн байхаар тохируулсан
бөгөөд лабын өөрийн ажлыг урьдчилж хийгээгүй:

| Лаб | Сэдэв | Одоо бэлэн байгаа зүйл |
|---|---|---|
| 7 | GitHub Actions CI | `backend/`-д `pip install -r requirements-dev.txt` → `pytest` нь `.env`, PostgreSQL-гүйгээр ажиллана; `frontend/`-д `npm ci` → `npm run build` |
| 8 | Dockerfile, Docker Compose | Бүх тохиргоо орчны хувьсагчаас (`.env`) уншигдана; `DB_HOST`-ийг compose-ын service нэрээр солиход болно |
| 9 | Minikube | `/api/health/` endpoint-ийг liveness/readiness probe болгон ашиглаж болно |
| 10 | Автомат тест | `pytest` + `pytest-django` тохируулагдсан; бизнес логик `services.py`-д тусдаа тул unit тестлэхэд хялбар |
| 11 | Статик шинжилгээ | Linter-ийг санаатайгаар тохируулаагүй — энэ лабаар нэмнэ |
| 13 | Prometheus, Grafana | `/metrics` endpoint-ийг энэ лабаар нэмнэ |
