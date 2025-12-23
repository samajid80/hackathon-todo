/**
 * Better-Auth configuration for JWT-based authentication
 *
 * This file configures Better-Auth to:
 * 1. Issue JWT tokens on successful login (EdDSA algorithm with asymmetric keys)
 * 2. Store user sessions in PostgreSQL database
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

console.log("[Auth Config] DATABASE_URL is set:", !!process.env.DATABASE_URL);
console.log("[Auth Config] DATABASE_URL starts with:", process.env.DATABASE_URL?.substring(0, 20));

// Create database connection using Kysely
// const db = new Kysely({
//   dialect: new PostgresDialect({
//     pool: new Pool({
//       connectionString: process.env.DATABASE_URL,
//       ssl: { rejectUnauthorized: false },
//     }),
//   }),
// });

// export const auth = betterAuth({
//   // Database configuration for user storage
//   database: {
//     db: db,
//     type: "postgres",
//   },

//   // Email/password authentication
//   emailAndPassword: {
//     enabled: true,
//     minPasswordLength: 8,
//     maxPasswordLength: 128,
//   },

//   // Session configuration
//   session: {
//     // Session expiration (24 hours)
//     expiresIn: 60 * 60 * 24, // 1 day in seconds

//     // Update session on activity
//     updateAge: 60 * 60, // Update every hour
//   },

//   // Advanced options
//   advanced: {
//     // Use secure cookies in production
//     useSecureCookies: process.env.NODE_ENV === "production",

//     // Cookie options
//     cookiePrefix: "hackathon-todo",
//   },

//   // Next.js integration
//   plugins: [
//     jwt(),  // JWT plugin uses EdDSA (asymmetric) by default
//             // Backend verifies tokens using public key from JWKS
//             // JWKS endpoint: http://localhost:3000/api/auth/jwks
//     nextCookies(), // Must be last
//   ],
// });


let db: Kysely<any> | null = null;

function getDb() {
  if (!db) {
    db = new Kysely({
      dialect: new PostgresDialect({
        pool: new Pool({
          connectionString: process.env.DATABASE_URL,
          ssl: { rejectUnauthorized: false },
          // Connection pool settings for Neon PostgreSQL
          max: 10, // Maximum number of connections in pool
          idleTimeoutMillis: 30000, // Close idle connections after 30 seconds
          connectionTimeoutMillis: 10000, // Timeout after 10 seconds if connection can't be established
        }),
      }),
    });
  }
  return db;
}

export const auth = betterAuth({
  // Database configuration for user storage
  database: {
    db: getDb(),
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
    cookiePrefix: "hackathon-todo",
  },

  // Next.js integration
  plugins: [
    jwt(),  // JWT plugin uses EdDSA (asymmetric) by default
            // Backend verifies tokens using public key from JWKS
            // JWKS endpoint: http://localhost:3000/api/auth/jwks
    nextCookies(), // Must be last
  ],
});

/**
 * Type definitions for Better-Auth session
 */
export type Session = typeof auth.$Infer.Session;
