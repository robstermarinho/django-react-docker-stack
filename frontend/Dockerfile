# frontend/Dockerfile (DEV)
FROM node:22-alpine

WORKDIR /app

# para o dev, vamos instalar deps no start (CMD) e manter node_modules em volume
EXPOSE 5173

CMD ["sh", "-lc", "npm ci || npm install && npm run dev -- --host"]