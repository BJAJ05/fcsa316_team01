# React app image, built in two stages.

# Stage 1: build the static files with Node. Dependencies first, for the build cache.
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# Stage 2: only the built files and nginx go into the final image (no Node, no node_modules).
FROM nginx:1.28-alpine
# nginx fills in ${BACKEND_URL} from the environment when the container starts.
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
# Docker Compose service name; Kubernetes overrides it (http://lms-backend:8000).
ENV BACKEND_URL=http://backend:8000
EXPOSE 80
