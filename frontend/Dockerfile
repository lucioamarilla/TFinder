FROM node:22-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
ARG VITE_MESAS_API=/mesas-api
ARG VITE_AUTH_MODE=api
ARG VITE_API_MODE=api
ENV VITE_MESAS_API=$VITE_MESAS_API
ENV VITE_AUTH_MODE=$VITE_AUTH_MODE
ENV VITE_API_MODE=$VITE_API_MODE
RUN npm run build

FROM nginx:1.27-alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
