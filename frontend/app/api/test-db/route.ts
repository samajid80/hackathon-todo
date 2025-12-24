/**
 * Database connection test endpoint
 * GET /api/test-db
 */

import { Pool } from 'pg';
import { NextResponse } from 'next/server';

export async function GET() {
  console.log('[Test DB] Starting database connection test...');
  console.log('[Test DB] DATABASE_URL configured:', !!process.env.DATABASE_URL);
  console.log('[Test DB] DATABASE_URL starts with:', process.env.DATABASE_URL?.substring(0, 50));

  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
    max: 1,
    connectionTimeoutMillis: 20000,
  });

  try {
    console.log('[Test DB] Attempting to connect...');
    const client = await pool.connect();
    console.log('[Test DB] Connected successfully!');

    const result = await client.query('SELECT NOW() as now, version() as version');
    console.log('[Test DB] Query executed successfully');

    client.release();
    await pool.end();

    return NextResponse.json({
      success: true,
      timestamp: result.rows[0].now,
      version: result.rows[0].version,
      message: 'Database connection successful!',
    });
  } catch (error) {
    console.error('[Test DB] Connection failed:', error);
    await pool.end();

    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : String(error),
      code: (error as any)?.code,
      stack: error instanceof Error ? error.stack : undefined,
    }, { status: 500 });
  }
}
