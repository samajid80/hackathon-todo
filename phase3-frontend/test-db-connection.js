const { Pool } = require('pg');
const fs = require('fs');

// Parse .env.local file
const envContent = fs.readFileSync('.env.local', 'utf8');
const envLines = envContent.split('\n');
let dbUrl = '';
for (const line of envLines) {
  if (line.startsWith('DATABASE_URL=')) {
    dbUrl = line.substring('DATABASE_URL='.length).trim();
    // Remove quotes if present
    dbUrl = dbUrl.replace(/^['"]|['"]$/g, '');
    break;
  }
}

if (!dbUrl) {
  console.error('DATABASE_URL not found in .env.local');
  process.exit(1);
}

console.log('Testing connection to:', dbUrl.substring(0, 30) + '...');

const pool = new Pool({
  connectionString: dbUrl,
  ssl: { rejectUnauthorized: false },
  connectionTimeoutMillis: 10000,
  statement_timeout: 30000
});

async function testConnection() {
  try {
    console.log('Attempting database connection...');
    const res = await pool.query('SELECT NOW() as current_time, version() as pg_version');
    console.log('✓ Database connection successful');
    console.log('Current time:', res.rows[0].current_time);
    console.log('PostgreSQL version:', res.rows[0].pg_version.substring(0, 50));

    // Check if Better Auth tables exist
    const tablesRes = await pool.query(`
      SELECT table_name
      FROM information_schema.tables
      WHERE table_schema = 'public'
      AND table_name IN ('user', 'session', 'account', 'verification')
      ORDER BY table_name
    `);

    console.log('\nBetter Auth tables found:');
    tablesRes.rows.forEach(row => console.log('  -', row.table_name));

    await pool.end();
    console.log('\n✓ Test completed successfully');
  } catch (err) {
    console.error('✗ Database connection failed:', err.message);
    console.error('Error code:', err.code);
    console.error('Error details:', err);
    process.exit(1);
  }
}

testConnection();
