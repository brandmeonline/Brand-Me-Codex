# brandme-gateway

brandme-gateway is the OAuth-protected edge API for Brand.Me, Inc. It ingests garment scan requests from mobile clients, resolves the authenticated scanner, enriches the payload with the deployment region, and publishes structured events to NATS JetStream for downstream processing across the MLS stack.

## Endpoints

### `GET /healthz`
Returns a simple health response `{ "status": "ok" }` for readiness and liveness probes.

### `POST /scan`
1. Requires a valid OAuth bearer token (stubbed in this scaffold).
2. Validates the request body matches `{ "garment_tag": string }`.
3. Extracts the `scanner_user_id` from the OAuth JWT (stubbed via middleware).
4. Attaches the default region defined by `DEFAULT_REGION` (defaults to `us-east1`).
5. Generates a `scan_id` (UUID v4).
6. Publishes the event `{ scan_id, scanner_user_id, garment_tag, timestamp, region_code }` to the `scan.requested` NATS subject using JetStream.
7. Returns HTTP 202 Accepted with `{ "scan_id": "..." }`.

## Configuration

Set the following environment variables before running the service:

- `OAUTH_CLIENT_ID`
- `OAUTH_CLIENT_SECRET`
- `DEFAULT_REGION` (default `us-east1`)
- `NATS_URL`
- `PORT` (optional, defaults to `8080`)

## Development

```bash
npm install
npm run dev
```

## Production Build

```bash
npm run build
npm run start
```

The service automatically publishes the `X-Region` header for downstream calls and emits structured logs for scan requests.
