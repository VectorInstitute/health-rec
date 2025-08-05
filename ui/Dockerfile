# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG FRONTEND_PORT
ARG BACKEND_PORT
ARG BACKEND_HOST
ARG NEXT_PUBLIC_MAPBOX_API_KEY
ENV NEXT_PUBLIC_FRONTEND_PORT=${FRONTEND_PORT} \
    NEXT_PUBLIC_BACKEND_PORT=${BACKEND_PORT} \
    NEXT_PUBLIC_BACKEND_HOST=${BACKEND_HOST} \
    NEXT_PUBLIC_MAPBOX_API_KEY=${NEXT_PUBLIC_MAPBOX_API_KEY}

RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

RUN addgroup -S nextjs && \
    adduser -S -G nextjs nextjs && \
    chown -R nextjs:nextjs /app

# Install sharp for production Image Optimization
RUN apk add --no-cache vips-dev
RUN npm install --platform=linuxmusl --arch=x64 sharp

USER nextjs

COPY --from=builder --chown=nextjs:nextjs /app/.next ./.next
COPY --from=builder --chown=nextjs:nextjs /app/node_modules ./node_modules
COPY --from=builder --chown=nextjs:nextjs /app/package.json ./package.json
COPY --from=builder --chown=nextjs:nextjs /app/public ./public

ARG FRONTEND_PORT
ENV NEXT_PUBLIC_FRONTEND_PORT=${FRONTEND_PORT}

EXPOSE ${FRONTEND_PORT}

CMD ["npm", "start"]
