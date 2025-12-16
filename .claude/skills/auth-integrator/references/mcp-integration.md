# Better Auth MCP Server Integration Guide

This guide explains how to effectively use the Better Auth MCP server when it's available in your environment.

## Overview

The Better Auth MCP server provides programmatic access to Better Auth configuration, schema validation, and code generation capabilities. When available, it significantly improves the accuracy and efficiency of authentication implementation.

## Available MCP Tools

### 1. Configuration Inspection

**Tool**: `better_auth_get_config`

**Purpose**: Retrieve current Better Auth configuration

**Usage**:
```javascript
const config = await better_auth_get_config()
```

**Returns**:
```json
{
  "database": {
    "provider": "postgres",
    "url": "postgresql://..."
  },
  "emailAndPassword": {
    "enabled": true,
    "requireEmailVerification": false
  },
  "socialProviders": {
    "google": {
      "clientId": "...",
      "enabled": true
    }
  },
  "session": {
    "expiresIn": 604800,
    "updateAge": 86400
  },
  "plugins": ["nextCookies"]
}
```

**When to use**:
- Starting a new authentication implementation
- Auditing existing setup
- Before making configuration changes
- Debugging authentication issues

### 2. Schema Validation

**Tool**: `better_auth_validate_schema`

**Purpose**: Verify database schema matches Better Auth requirements

**Usage**:
```javascript
const validation = await better_auth_validate_schema({
  databaseUrl: process.env.DATABASE_URL
})
```

**Returns**:
```json
{
  "valid": false,
  "issues": [
    {
      "table": "user",
      "column": "email_verified",
      "message": "Column missing or wrong type",
      "suggestion": "ALTER TABLE user ADD COLUMN email_verified BOOLEAN DEFAULT false"
    },
    {
      "table": "session",
      "message": "Table does not exist",
      "suggestion": "CREATE TABLE session (...)"
    }
  ],
  "missingTables": ["session", "account", "verification"],
  "missingColumns": {
    "user": ["email_verified", "image"]
  }
}
```

**When to use**:
- After database migrations
- Before deploying authentication
- When troubleshooting connection issues
- During initial setup

### 3. Provider Information

**Tool**: `better_auth_list_providers`

**Purpose**: Get available OAuth providers and their configuration requirements

**Usage**:
```javascript
const providers = await better_auth_list_providers()
```

**Returns**:
```json
{
  "available": [
    {
      "id": "google",
      "name": "Google",
      "requiresClientId": true,
      "requiresClientSecret": true,
      "scopes": ["profile", "email"],
      "authorizationUrl": "https://accounts.google.com/o/oauth2/v2/auth",
      "tokenUrl": "https://oauth2.googleapis.com/token"
    },
    {
      "id": "github",
      "name": "GitHub",
      "requiresClientId": true,
      "requiresClientSecret": true,
      "scopes": ["read:user", "user:email"]
    }
  ],
  "configured": ["google"]
}
```

**When to use**:
- Adding new OAuth providers
- Checking provider setup requirements
- Debugging OAuth flows
- Planning authentication methods

### 4. Type Generation

**Tool**: `better_auth_generate_types`

**Purpose**: Generate TypeScript types based on your configuration

**Usage**:
```javascript
const types = await better_auth_generate_types({
  includeSession: true,
  includeUser: true
})
```

**Returns**:
```typescript
export interface Session {
  id: string
  userId: string
  expiresAt: Date
  token: string
  createdAt: Date
  updatedAt: Date
}

export interface User {
  id: string
  email: string
  emailVerified: boolean
  name: string | null
  image: string | null
  createdAt: Date
  updatedAt: Date
}

export interface AuthSession {
  session: Session
  user: User
}
```

**When to use**:
- Setting up TypeScript project
- After schema changes
- Ensuring type safety across frontend/backend
- During initial configuration

### 5. Code Generation

**Tool**: `better_auth_generate_config`

**Purpose**: Generate Better Auth configuration code based on requirements

**Usage**:
```javascript
const code = await better_auth_generate_config({
  providers: ["google", "github"],
  database: "postgres",
  emailPassword: true,
  plugins: ["nextCookies", "twoFactor"]
})
```

**Returns**:
```typescript
import { betterAuth } from "better-auth"
import { nextCookies } from "better-auth/next-js"
import { twoFactor } from "better-auth/plugins"

export const auth = betterAuth({
  database: {
    provider: "postgres",
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
  },
  secret: process.env.BETTER_AUTH_SECRET!,
  plugins: [nextCookies(), twoFactor()],
})
```

**When to use**:
- Starting new project
- Migrating from another auth system
- Adding new authentication methods
- Updating configuration

## Integration Workflow

### Step 1: Check Availability

Before using MCP tools, verify they're available:

```typescript
async function checkMCPAvailability(): Promise<boolean> {
  try {
    // Try to call a simple MCP tool
    await better_auth_get_config()
    return true
  } catch (error) {
    console.log('Better Auth MCP not available, using fallback')
    return false
  }
}
```

### Step 2: Inspect Current Setup

When MCP is available, start by inspecting the current configuration:

```typescript
async function analyzeAuthSetup() {
  // Get current configuration
  const config = await better_auth_get_config()
  
  // Validate database schema
  const validation = await better_auth_validate_schema({
    databaseUrl: process.env.DATABASE_URL
  })
  
  // Check configured providers
  const providers = await better_auth_list_providers()
  
  return {
    config,
    validation,
    providers
  }
}
```

### Step 3: Generate Code Based on Findings

Use the inspection results to inform code generation:

```typescript
async function generateAuthImplementation(requirements) {
  const analysis = await analyzeAuthSetup()
  
  // If schema is invalid, generate migration
  if (!analysis.validation.valid) {
    console.log('Database schema needs updates:')
    analysis.validation.issues.forEach(issue => {
      console.log(`- ${issue.table}: ${issue.message}`)
      console.log(`  Fix: ${issue.suggestion}`)
    })
  }
  
  // Generate configuration matching requirements
  const configCode = await better_auth_generate_config({
    providers: requirements.oauthProviders,
    database: analysis.config.database.provider,
    emailPassword: requirements.emailPassword,
    plugins: requirements.plugins
  })
  
  // Generate types
  const types = await better_auth_generate_types({
    includeSession: true,
    includeUser: true
  })
  
  return { configCode, types }
}
```

### Step 4: Validate Implementation

After generating code, validate it:

```typescript
async function validateImplementation() {
  // Re-validate schema after changes
  const validation = await better_auth_validate_schema({
    databaseUrl: process.env.DATABASE_URL
  })
  
  if (validation.valid) {
    console.log('✓ Database schema is valid')
  } else {
    console.log('✗ Schema validation failed:')
    validation.issues.forEach(issue => {
      console.log(`  - ${issue.message}`)
    })
  }
  
  return validation.valid
}
```

## Error Handling

MCP tools may fail or be unavailable. Always implement fallbacks:

```typescript
async function safeGetConfig() {
  try {
    return await better_auth_get_config()
  } catch (error) {
    console.warn('MCP tool unavailable, using defaults')
    return {
      database: { provider: 'postgres' },
      emailAndPassword: { enabled: true },
      socialProviders: {},
      plugins: []
    }
  }
}
```

## Best Practices

### 1. Progressive Enhancement

Use MCP tools to enhance, not replace, your implementation:

```typescript
async function implementAuth(requirements) {
  const useMCP = await checkMCPAvailability()
  
  if (useMCP) {
    // Enhanced path with MCP
    const analysis = await analyzeAuthSetup()
    return generateFromAnalysis(analysis, requirements)
  } else {
    // Fallback path
    return generateFromRequirements(requirements)
  }
}
```

### 2. Cache MCP Results

MCP calls can be expensive. Cache results when appropriate:

```typescript
let configCache: any = null
let cacheTime: number = 0
const CACHE_TTL = 60000 // 1 minute

async function getCachedConfig() {
  const now = Date.now()
  if (configCache && (now - cacheTime) < CACHE_TTL) {
    return configCache
  }
  
  configCache = await better_auth_get_config()
  cacheTime = now
  return configCache
}
```

### 3. Validate User Input

Don't blindly trust MCP results. Validate against requirements:

```typescript
async function validateConfiguration(requirements) {
  const config = await better_auth_get_config()
  
  // Check if required providers are configured
  for (const provider of requirements.providers) {
    if (!config.socialProviders?.[provider]) {
      console.warn(`Required provider ${provider} not configured`)
    }
  }
  
  // Check if email/password is enabled when required
  if (requirements.emailPassword && !config.emailAndPassword?.enabled) {
    console.warn('Email/password authentication not enabled')
  }
}
```

### 4. Provide Clear Feedback

When MCP tools reveal issues, provide actionable feedback:

```typescript
async function diagnoseAuthIssues() {
  const validation = await better_auth_validate_schema({
    databaseUrl: process.env.DATABASE_URL
  })
  
  if (!validation.valid) {
    console.log('\n⚠️  Authentication Setup Issues Found:\n')
    
    if (validation.missingTables.length > 0) {
      console.log('Missing tables:')
      validation.missingTables.forEach(table => {
        console.log(`  - ${table}`)
      })
      console.log('\nRun database migrations to create these tables.')
    }
    
    if (Object.keys(validation.missingColumns).length > 0) {
      console.log('\nMissing columns:')
      Object.entries(validation.missingColumns).forEach(([table, columns]) => {
        console.log(`  ${table}:`)
        columns.forEach(col => console.log(`    - ${col}`))
      })
      console.log('\nUpdate your schema to include these columns.')
    }
    
    console.log('\n💡 Tip: Run `npx better-auth migrate` to fix schema issues.')
  }
}
```

## Common Patterns

### Pattern 1: Configuration Sync Check

Ensure frontend and backend configurations match:

```typescript
async function checkConfigSync() {
  const frontendConfig = await better_auth_get_config()
  const backendSecret = process.env.BETTER_AUTH_SECRET
  
  if (!backendSecret) {
    throw new Error('BETTER_AUTH_SECRET not set in backend')
  }
  
  // Check if secrets could match (can't compare directly for security)
  console.log('✓ Backend secret is configured')
  
  // Check provider consistency
  const configuredProviders = Object.keys(frontendConfig.socialProviders || {})
  console.log(`✓ Frontend has ${configuredProviders.length} OAuth providers configured`)
  
  return {
    frontendProviders: configuredProviders,
    backendSecretConfigured: !!backendSecret
  }
}
```

### Pattern 2: Migration Generation

Generate database migrations based on schema validation:

```typescript
async function generateMigrations() {
  const validation = await better_auth_validate_schema({
    databaseUrl: process.env.DATABASE_URL
  })
  
  if (validation.valid) {
    console.log('No migrations needed')
    return []
  }
  
  const migrations = []
  
  // Generate CREATE TABLE statements
  for (const table of validation.missingTables) {
    const sql = validation.issues
      .find(i => i.table === table && i.suggestion.includes('CREATE TABLE'))
      ?.suggestion
    
    if (sql) migrations.push({ table, sql, type: 'CREATE_TABLE' })
  }
  
  // Generate ALTER TABLE statements
  for (const [table, columns] of Object.entries(validation.missingColumns)) {
    for (const column of columns) {
      const issue = validation.issues.find(
        i => i.table === table && i.column === column
      )
      if (issue?.suggestion) {
        migrations.push({ table, column, sql: issue.suggestion, type: 'ADD_COLUMN' })
      }
    }
  }
  
  return migrations
}
```

## Troubleshooting

### MCP Server Not Responding

If MCP tools time out or fail:

1. Check Claude Code configuration for Better Auth MCP
2. Verify the MCP server is running
3. Check logs for connection errors
4. Fall back to manual implementation

### Schema Validation Failures

If schema validation repeatedly fails:

1. Check database connection string
2. Verify database permissions
3. Run Better Auth migrations manually
4. Compare with Better Auth documentation

### Configuration Mismatches

If frontend and backend configs don't align:

1. Use MCP to inspect both configurations
2. Ensure `BETTER_AUTH_SECRET` matches exactly
3. Verify environment variables are loaded
4. Check for typos in provider names

## Summary

The Better Auth MCP server is a powerful tool for authentication implementation, but should be used as an enhancement rather than a requirement. Always:

- Check availability before using
- Implement graceful fallbacks
- Cache results when appropriate
- Validate all generated code
- Provide clear error messages
- Test thoroughly before deployment
