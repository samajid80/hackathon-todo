const { Pool } = require('pg');
const fs = require('fs');

// Parse .env.local
const envContent = fs.readFileSync('.env.local', 'utf8');
let dbUrl = '';
for (const line of envContent.split('\n')) {
  if (line.startsWith('DATABASE_URL=')) {
    dbUrl = line.substring('DATABASE_URL='.length).trim().replace(/^['"]|['"]$/g, '');
    break;
  }
}

console.log('Original URL (first 50 chars):', dbUrl.substring(0, 50));

// Neon recommends using ?sslmode=require and connection pooling
// Try adding options parameter to force IPv4
const url = new URL(dbUrl);

// Force specific connection parameters for Neon
url.searchParams.set('sslmode', 'require');
url.searchParams.delete('sslaccept');  // Remove if exists
url.searchParams.delete('sslcert');    // Remove if exists

const finalUrl = url.toString();
console.log('Modified URL (first 50 chars):', finalUrl.substring(0, 50));

const pool = new Pool({
  connectionString: finalUrl,
  ssl: {
    rejectUnauthorized: false
  },
  connectionTimeoutMillis: 10000,
  // Try with minimal pool size
  max: 1,
  min: 0,
  idleTimeoutMillis: 30000
});

async function test() {
  try {
    console.log('\nAttempting connection...');
    const client = await pool.connect();
    console.log('✓ Connected successfully');
    
    const res = await client.query('SELECT NOW() as time');
    console.log('✓ Query executed:', res.rows[0].time);
    
    client.release();
    await pool.end();
    console.log('✓ Test passed');
  } catch (err) {
    console.error('✗ Connection failed:', err.message);
    console.error('Error code:', err.code);
    process.exit(1);
  }
}

test();
