/**
 * Copyright (c) Brand.Me, Inc. All rights reserved.
 */

import { connect, JSONCodec, JetStreamClient, NatsConnection } from 'nats';

export interface ScanRequestedEvent {
  scan_id: string;
  scanner_user_id: string;
  garment_tag: string;
  timestamp: string;
  region_code: string;
}

const jsonCodec = JSONCodec<ScanRequestedEvent>();

let connectionPromise: Promise<NatsConnection> | undefined;

async function getConnection(): Promise<NatsConnection> {
  if (!connectionPromise) {
    const url = process.env.NATS_URL;
    if (!url) {
      throw new Error('NATS_URL is not configured');
    }

    connectionPromise = connect({ servers: url });
  }

  return connectionPromise;
}

async function getJetStream(): Promise<JetStreamClient> {
  const connection = await getConnection();
  return connection.jetstream();
}

export async function publishScanRequested(eventPayload: ScanRequestedEvent): Promise<void> {
  const jetStream = await getJetStream();
  await jetStream.publish('scan.requested', jsonCodec.encode(eventPayload));
}

export async function closeNatsConnection(): Promise<void> {
  if (connectionPromise) {
    const connection = await connectionPromise;
    await connection.drain();
    connectionPromise = undefined;
  }
}
