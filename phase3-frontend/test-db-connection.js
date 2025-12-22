/**
 * Test database connection to Neon PostgreSQL.
 *
 * This script helps diagnose connection issues, especially with Neon's
 * free tier sleep mode.
 *
 * Usage:
 *   DATABASE_URL="postgresql://..." node test-db-connection.js
 * Or:
 *   source .env.local && node test-db-connection.js
 */

const { Pool } = require('pg');

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
  max: 3,
  connectionTimeoutMillis: 30000,
  statement_timeout: 20000,
  keepAlive: true,
});

async function testConnection() {
  console.log('[DB Test] Starting connection test...');
  console.log('[DB Test] DATABASE_URL:', process.env.DATABASE_URL?.substring(0, 30) + '...');

  try {
    const startTime = Date.now();
    const client = await pool.connect();
    const connectionTime = Date.now() - startTime;

    console.log(`[DB Test] ✓ Connected successfully in ${connectionTime}ms`);

    // Test query
    const queryStart = Date.now();
    const result = await client.query('SELECT NOW()');
    const queryTime = Date.now() - queryStart;

    console.log(`[DB Test] ✓ Query executed in ${queryTime}ms`);
    console.log('[DB Test] Server time:', result.rows[0].now);

    // Test users table
    const usersResult = await client.query('SELECT COUNT(*) FROM users');
    console.log('[DB Test] ✓ Users table accessible, count:', usersResult.rows[0].count);

    // Test session table (if exists)
    try {
      const sessionResult = await client.query('SELECT COUNT(*) FROM session');
      console.log('[DB Test] ✓ Session table accessible, count:', sessionResult.rows[0].count);
    } catch (e) {
      console.log('[DB Test] ⚠ Session table not found (this is OK for first run)');
    }

    client.release();
    console.log('[DB Test] ✓ Connection released');
    console.log('[DB Test] All tests passed!');

  } catch (error) {
    console.error('[DB Test] ✗ Connection failed:', error.message);
    if (error.code) {
      console.error('[DB Test] Error code:', error.code);
    }
    throw error;
  } finally {
    await pool.end();
    console.log('[DB Test] Pool closed');
  }
}

testConnection()
  .then(() => {
    console.log('\n[DB Test] SUCCESS - Database is accessible');
    process.exit(0);
  })
  .catch((error) => {
    console.error('\n[DB Test] FAILED - See errors above');
    process.exit(1);
  });
