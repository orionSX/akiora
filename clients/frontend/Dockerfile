FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json ./

# Если есть pnpm-lock.yaml - удаляем его
RUN if [ -f pnpm-lock.yaml ]; then rm -f pnpm-lock.yaml; fi

# Устанавливаем зависимости через npm install (создаст package-lock.json)
RUN npm install --legacy-peer-deps

COPY . .

RUN npm run build

FROM nginx:1.27-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
