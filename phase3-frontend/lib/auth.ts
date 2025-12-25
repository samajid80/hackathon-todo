/**
 * Better-Auth configuration for Phase 3 Frontend (JWT-based authentication).
 *
 * This file configures Better-Auth to:
 * 1. Issue JWT tokens on successful login (EdDSA algorithm with asymmetric keys)
 * 2. Store user sessions in PostgreSQL database (shared with Phase 2)
 * 3. Provide public keys via JWKS endpoint for token verification
 * 4. Backend verifies tokens using public key from JWKS
 */

import { betterAuth } from "better-auth";
import { nextCookies } from "better-auth/next-js";
import { jwt } from "better-auth/plugins";
import { Kysely, PostgresDialect } from "kysely";
import { Pool } from "pg";

if (!process.env.BETTER_AUTH_SECRET) {
  throw new Error("BETTER_AUTH_SECRET environment variable is required");
}

if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL environment variable is required");
}

console.log("[Phase3 Auth Config] DATABASE_URL is set:", !!process.env.DATABASE_URL);
console.log("[Phase3 Auth Config] DATABASE_URL starts with:", process.env.DATABASE_URL?.substring(0, 20));

// Global singleton for database connection that persists across Next.js contexts
declare global {
  var __phase3DbPool: Kysely<any> | undefined;
}

/**
 * Get or create the global database connection pool.
 * Uses a singleton pattern to prevent multiple pool creation.
 *
 * This ensures only ONE pool is created even with concurrent requests during
 * Next.js hot module reloading by checking globalThis first.
 */
function getDbSync(): Kysely<any> {
  // If already initialized, return immediately
  if (globalThis.__phase3DbPool) {
    return globalThis.__phase3DbPool;
  }

  // Create the pool (synchronous operation)
  const baseConnectionString = process.env.DATABASE_URL || '';

  // Add connection parameters optimized for Neon serverless
  const url = new URL(baseConnectionString);
  url.searchParams.set('sslmode', 'require'); // Required for Neon
  url.searchParams.set('statement_timeout', '30000'); // 30 second query timeout
  url.searchParams.set('connect_timeout', '15'); // 15 second connection timeout
  url.searchParams.set('application_name', 'phase3-frontend');
  const connectionString = url.toString();

  console.log('[Phase3 Auth] Creating database pool (singleton)');

  // Create the Pool instance
  const pool = new Pool({
    connectionString: connectionString,
    ssl: { rejectUnauthorized: false },
    // Conservative settings optimized for Neon serverless
    max: 5, // Limit concurrent connections
    min: 0, // Don't maintain idle connections (create on demand)
    idleTimeoutMillis: 30000, // 30 seconds
    connectionTimeoutMillis: 20000, // 20 seconds (allow more time for Neon)
    // Keepalive for serverless environment
    keepAlive: true,
    keepAliveInitialDelayMillis: 10000,
  });

  const db = new Kysely({
    dialect: new PostgresDialect({ pool }),
  });

  // Store in globalThis immediately (synchronous)
  globalThis.__phase3DbPool = db;

  // Warmup asynchronously in background (don't block)
  // Use the pool directly for a simple health check
  pool.query('SELECT 1 as health_check')
    .then(() => {
      console.log('[Phase3 Auth] ✓ Database pool warmed up');
    })
    .catch((err) => {
      console.error('[Phase3 Auth] ✗ Warmup failed (will retry on first request):', err?.message);
    });

  console.log('[Phase3 Auth] Pool created (max:5, min:0, on-demand connections)');

  return db;
}

export const auth = betterAuth({
  // Database configuration for user storage (shared with Phase 2)
  database: {
    db: getDbSync(),
    type: "postgres",
  },

  // Email/password authentication
  emailAndPassword: {
    enabled: true,
    minPasswordLength: 8,
    maxPasswordLength: 128,
  },

  // Session configuration
  session: {
    // Session expiration (24 hours)
    expiresIn: 60 * 60 * 24, // 1 day in seconds

    // Update session on activity
    updateAge: 60 * 60, // Update every hour
  },

  // Advanced options
  advanced: {
    // Use secure cookies in production
    useSecureCookies: process.env.NODE_ENV === "production",

    // Cookie options
    cookiePrefix: "phase3-hackathon-todo",
  },

  // Next.js integration with JWT plugin
  plugins: [
    jwt(),  // JWT plugin uses EdDSA (asymmetric) by default
            // Backend verifies tokens using public key from JWKS
            // JWKS endpoint: http://localhost:3001/api/auth/jwks
    nextCookies(), // Must be last
  ],
});

/**
 * Type definitions for Better-Auth session
 */
export type Session = typeof auth.$Infer.Session;
