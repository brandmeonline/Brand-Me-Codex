# Copyright (c) Brand.Me, Inc. All rights reserved.
FROM node:18-alpine

WORKDIR /app

ENV NODE_ENV=production

COPY package.json ./
COPY tsconfig.json ./
RUN npm install

COPY src ./src

RUN npm run build && npm prune --production

EXPOSE 8080

CMD ["node", "dist/server.js"]
