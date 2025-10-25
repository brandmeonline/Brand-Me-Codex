/**
 * Copyright (c) Brand.Me, Inc. All rights reserved.
 */

import { FastifyReply, FastifyRequest, preHandlerHookHandler } from 'fastify';

export interface AuthenticatedUser {
  user_id: string;
}

declare module 'fastify' {
  interface FastifyRequest {
    user?: AuthenticatedUser;
  }
}

function extractUserIdFromAuth(authorizationHeader?: string): string | null {
  if (!authorizationHeader) {
    return null;
  }
  // TODO: Replace with real OAuth validation using the configured provider.
  return 'demo-user-uuid';
}

async function handleUnauthorized(reply: FastifyReply): Promise<void> {
  reply.code(401).send({ error: 'unauthorized' });
}

export function oauthPreHandler(): preHandlerHookHandler {
  return async (request: FastifyRequest, reply: FastifyReply): Promise<void> => {
    const authorizationHeader = request.headers.authorization;
    const userId = extractUserIdFromAuth(authorizationHeader);

    if (!userId) {
      await handleUnauthorized(reply);
      return;
    }

    request.user = { user_id: userId };
  };
}
