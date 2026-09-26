FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
ARG VITE_MESAS_API=/mesas-api
ARG VITE_BUILDS_API=/builds-api
ARG VITE_FEED_API=/feed-api
ARG VITE_NOTIF_API=/notif-api
ENV VITE_MESAS_API=$VITE_MESAS_API
ENV VITE_BUILDS_API=$VITE_BUILDS_API
ENV VITE_FEED_API=$VITE_FEED_API
ENV VITE_NOTIF_API=$VITE_NOTIF_API
RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
