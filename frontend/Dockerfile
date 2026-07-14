FROM node:18-alpine AS builder

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependências
RUN npm ci

# Copiar código
COPY . .

# Build
RUN npm run build

# Runtime
FROM node:18-alpine

WORKDIR /app

# Instalar serve para servir a app
RUN npm install -g serve

# Copiar build da etapa anterior
COPY --from=builder /app/dist ./dist

# Expor porta
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# Comando para iniciar
CMD ["serve", "-s", "dist", "-l", "3000"]
