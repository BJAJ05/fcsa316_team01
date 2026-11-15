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

### Kubernetes (Minikube)

Дээрх Docker image-үүдийг локал Kubernetes кластер (Minikube) дээр ажиллуулна: PostgreSQL, backend-ийн
**3 хуулбар** (replica), frontend. Тохиргооны файлууд [`k8s/`](k8s/) хавтсанд. Docker, `minikube`,
`kubectl` хэрэгтэй (`minikube version`, `kubectl version --client`).

1. Image-үүдийг үүсгээд (`docker compose build`), кластерыг асааж, image-үүдийг кластер руу хуулна:
   ```bash
   minikube start --driver=docker --cpus=2 --memory=2500   # кластер ~1.3 GB санах ой хэрэглэнэ
   minikube image load lms-backend:1.0
   minikube image load lms-frontend:1.0
   ```
2. Нууц утгуудыг (Secret) нэг удаа үүсгэнэ. Утгууд нь санамсаргүй, кластер дотор л хадгалагдана
   (git-д орохгүй):
   ```bash
   kubectl create secret generic lms-secrets \
     --from-literal=DJANGO_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')" \
     --from-literal=DB_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_hex(16))')"
   ```
3. Дарааллаар нь ажиллуулна (өгөгдлийн сан → migration → backend → frontend):
   ```bash
   kubectl apply -f k8s/configmap.yaml -f k8s/postgres.yaml
   kubectl rollout status deploy/lms-db
   kubectl apply -f k8s/migrate-job.yaml
   kubectl wait --for=condition=complete job/lms-migrate --timeout=180s
   kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
   kubectl apply -f k8s/frontend.yaml
   kubectl get pods   # lms-backend-... гурван pod: Running, 1/1
   ```
4. `minikube service lms-frontend` → хөтөч дээр апп нээгдэнэ (гурван ✓). API-г шууд шалгах:
   `curl $(minikube service lms-backend --url)/api/health/`

Нэг backend pod-ийг устгавал (`kubectl delete pod lms-backend-...`) Kubernetes оронд нь шинэ pod үүсгэж,
3 хуулбарыг хадгална (self-healing). Үүнийг `kubectl get pods -w`-ээр харна.

| Файл | Агуулга |
|---|---|
| `configmap.yaml` | Нууц биш тохиргоо (`DB_HOST=lms-db`, `DEBUG=False` г.м.) |
| `postgres.yaml` | PostgreSQL 16: 1Gi volume, Deployment, кластер доторх Service `lms-db` |
| `migrate-job.yaml` | `migrate`-ийг нэг удаа ажиллуулах Job |
| `deployment.yaml` | Backend, 3 replica; readiness probe `/api/health/`, liveness probe TCP 8000 |
| `service.yaml` | Backend-ийн NodePort Service (кластер дотор `lms-backend:8000`, гаднаас 30800 порт) |
| `frontend.yaml` | nginx + React, NodePort Service (гаднаас 30080 порт) |

| Комманд | Юу хийх вэ |
|---|---|
| `kubectl get pods` | Pod-уудын төлөв |
| `kubectl logs deploy/lms-backend` | Backend-ийн лог (нэг pod-ийнх) |
| `kubectl scale deploy/lms-backend --replicas=5` | Хуулбарын тоог өөрчлөх |
| `minikube stop` | Кластерыг зогсоох (өгөгдөл хадгалагдана) |
| `minikube delete` | Кластерыг бүхэлд нь устгах |

- **Код өөрчилсний дараа:** шинэ tag-аар image үүсгэнэ (`docker build -t lms-backend:1.1 backend`), дараа нь
  `minikube image load lms-backend:1.1`. `deployment.yaml`, `migrate-job.yaml`-ийн `image:`-ийг сольж
  дахин apply хийнэ.
- **Шинэ migration нэмэгдвэл:** `kubectl delete job lms-migrate`, дараа нь `kubectl apply -f k8s/migrate-job.yaml`.
- **Secret-ийн `DB_PASSWORD`-ийг сольвол:** PostgreSQL анхны нууц үгээ хадгалсаар байна. Тиймээс
  `kubectl delete -f k8s/postgres.yaml` (өгөгдөл устна) хийгээд дахин apply хийнэ.
- **Windows (PowerShell):** мөр таслах `\`-ийн оронд `` ` ``, `python3`-ийн оронд `python` бичнэ.
  `minikube service ...` нь tunnel нээдэг тул terminal-ыг нээлттэй байлгана.

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
| 9 | Minikube | **Хийгдсэн:** `k8s/` — PostgreSQL (volume), migration Job, backend 3 replica (`/api/health/` readiness probe), NodePort Service-үүд, frontend — дээрх "Kubernetes (Minikube)" хэсгийг үзнэ үү |
| 10 | Автомат тест | `pytest` + `pytest-django` тохируулагдсан; бизнес логик `services.py`-д тусдаа тул unit тестлэхэд хялбар |
| 11 | Статик шинжилгээ | Linter-ийг санаатайгаар тохируулаагүй — энэ лабаар нэмнэ |
| 13 | Prometheus, Grafana | `/metrics` endpoint-ийг энэ лабаар нэмнэ |
