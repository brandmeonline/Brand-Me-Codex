/**
 * Copyright (c) Brand.Me, Inc. All rights reserved.
 */

import fastify, { FastifyInstance } from 'fastify';
import dotenv from 'dotenv';
import { randomUUID } from 'node:crypto';
import { v4 as uuidv4 } from 'uuid';
import { oauthPreHandler } from './auth.js';
import { closeNatsConnection, publishScanRequested } from './natsClient.js';

dotenv.config();

const DEFAULT_REGION = process.env.DEFAULT_REGION ?? 'us-east1';
const PORT = Number(process.env.PORT ?? 8080);

interface ScanRequestBody {
  garment_tag: string;
}

function buildServer(): FastifyInstance {
  const server = fastify({
    logger: true,
    disableRequestLogging: false,
  });

  server.addHook('onRequest', async (request, reply) => {
    const incomingRequestId = request.headers['x-request-id'];
    const requestId = typeof incomingRequestId === 'string' ? incomingRequestId : randomUUID();
    if (!incomingRequestId) {
      request.headers['x-request-id'] = requestId;
    }
    reply.header('X-Request-Id', requestId);
  });

  server.get('/healthz', async () => ({ status: 'ok' }));

  server.post<{ Body: ScanRequestBody }>('/scan', {
    schema: {
      body: {
        type: 'object',
        required: ['garment_tag'],
        additionalProperties: false,
        properties: {
          garment_tag: { type: 'string', minLength: 1 },
        },
      },
      response: {
        202: {
          type: 'object',
          properties: {
            scan_id: { type: 'string' },
          },
          required: ['scan_id'],
        },
      },
    },
    preHandler: oauthPreHandler(),
  }, async (request, reply) => {
    const { garment_tag } = request.body;
    const userId = request.user?.user_id;

    if (!userId) {
      request.log.warn('Authenticated user not found in request context');
      return reply.code(401).send({ error: 'unauthorized' });
    }

    const scanId = uuidv4();
    const regionCode = DEFAULT_REGION;
    const timestamp = new Date().toISOString();

    try {
      await publishScanRequested({
        scan_id: scanId,
        scanner_user_id: userId,
        garment_tag,
        timestamp,
        region_code: regionCode,
      });
      request.log.info({ scan_id: scanId, scanner_user_id: userId, garment_tag, region_code: regionCode }, 'Published scan.requested event');
    } catch (error) {
      request.log.error({ err: error, scan_id: scanId }, 'Failed to publish scan.requested event');
      return reply.code(502).send({ error: 'failed_to_publish_event' });
    }

    reply.header('X-Region', regionCode);
    return reply.code(202).send({ scan_id: scanId });
  });

  return server;
}

const server = buildServer();

const start = async (): Promise<void> => {
  try {
    await server.listen({ port: PORT, host: '0.0.0.0' });
    server.log.info(`brandme-gateway listening on port ${PORT}`);
  } catch (err) {
    server.log.error(err);
    process.exit(1);
  }
};

start();

const shutdown = async (): Promise<void> => {
  server.log.info('Shutting down brandme-gateway');
  try {
    await closeNatsConnection();
    await server.close();
  } catch (err) {
    server.log.error({ err }, 'Error during shutdown');
  } finally {
    process.exit(0);
  }
};

process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
