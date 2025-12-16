# Auth Integrator Skill - Enhanced with MCP Support

## What's New

This enhanced version of your auth-integrator skill now fully leverages the Better Auth MCP server you have installed in Claude Code. Here are the key improvements:

### 1. **MCP-Aware Workflow**
The skill now intelligently checks for Better Auth MCP server availability and uses it to:
- Inspect existing Better Auth configurations
- Validate database schemas
- Generate type-safe code based on your actual setup
- Ensure consistency between frontend and backend

### 2. **Progressive Enhancement**
The skill works with or without MCP:
- **With MCP**: Gets real configuration data, validates schemas, generates accurate code
- **Without MCP**: Falls back to best-practice patterns and manual implementation

### 3. **Comprehensive Documentation**
Three new reference files provide detailed guidance:
- `references/examples.md` - Complete working code examples
- `references/mcp-integration.md` - Detailed MCP tool usage guide
- `scripts/jwt-verify-test.py` - Testing script for JWT verification

## File Structure

```
auth-integrator-enhanced/
├── SKILL.md                           # Main skill instructions (enhanced with MCP)
├── LICENSE.txt                        # MIT License
├── references/
│   ├── examples.md                    # 6 complete implementation examples
│   └── mcp-integration.md            # MCP server integration guide
└── scripts/
    └── jwt-verify-test.py            # JWT verification test script
```

## How It Works with Better Auth MCP

### Step 1: Availability Check
When you use this skill, Claude will first check if the Better Auth MCP server is available:

```javascript
// Claude checks for MCP tools like:
- better_auth_get_config
- better_auth_validate_schema
- better_auth_list_providers
```

### Step 2: Configuration Inspection
If MCP is available, Claude inspects your current setup:
- Retrieves existing Better Auth configuration
- Validates database schema against requirements
- Lists configured OAuth providers
- Checks for any configuration mismatches

### Step 3: Smart Code Generation
Claude uses the MCP data to generate code that:
- Matches your exact configuration
- Is type-safe based on your schema
- Includes only the providers you have configured
- Fixes any schema issues it discovers

### Step 4: Validation
After generation, Claude can use MCP to validate:
- Schema correctness
- Configuration consistency
- Missing tables or columns

## Key Features

### 1. Enhanced SKILL.md
The main skill file now includes:
- **Step 1**: MCP availability check and context gathering
- **MCP Tool Usage Guide**: When and how to use each MCP tool
- **Conditional workflows**: Different paths for MCP vs. non-MCP scenarios
- **Comprehensive error handling**: What to do when things go wrong

### 2. Complete Examples (`references/examples.md`)
Six detailed examples covering:
1. Basic email/password authentication
2. OAuth + email/password (Google, GitHub)
3. Authenticated API client with auto-retry
4. Role-based access control (RBAC)
5. Using Better Auth MCP server tools
6. Database models with relationships

### 3. MCP Integration Guide (`references/mcp-integration.md`)
Detailed documentation of:
- All available MCP tools
- When to use each tool
- Error handling strategies
- Common patterns and workflows
- Troubleshooting tips

### 4. Testing Script (`scripts/jwt-verify-test.py`)
A Python script that:
- Generates test JWT tokens
- Verifies token signatures
- Tests with wrong secrets (should fail)
- Tests expired tokens (should fail)
- Provides detailed output for debugging

## Usage Examples

### Example 1: New Project Setup

**You say:**
"Set up authentication for my Next.js + FastAPI app using Better Auth with Google OAuth"

**Claude will:**
1. Check for Better Auth MCP server
2. If available: Inspect current configuration
3. Generate frontend `auth.ts` with Google OAuth
4. Generate backend JWT verification
5. Create protected API routes
6. Validate schema with MCP
7. Provide migration SQL if needed

### Example 2: Adding to Existing Project

**You say:**
"Add JWT authentication to my existing /api/tasks endpoint"

**Claude will:**
1. Use MCP to check current Better Auth setup
2. Inspect existing tasks route
3. Add JWT verification dependency
4. Modify route to filter by user_id
5. Test with verification script

### Example 3: Debugging Auth Issues

**You say:**
"My auth tokens aren't working, help me debug"

**Claude will:**
1. Use MCP to validate schema
2. Check for configuration mismatches
3. Verify secret key consistency
4. Run JWT test script
5. Identify specific issues
6. Provide fixes

## How to Use This Skill

### Option 1: In Claude Code (Recommended)
Since you have Better Auth MCP server installed in Claude Code, this is the ideal environment:

1. Open Claude Code in your project
2. Reference this skill: "Use the auth-integrator skill to set up authentication"
3. Claude will automatically use the MCP server

### Option 2: Manual Package Installation
If you want to package and install this skill:

1. Use the skill-creator's packaging script:
   ```bash
   python /mnt/skills/examples/skill-creator/scripts/package_skill.py \
     /mnt/user-data/outputs/auth-integrator-enhanced
   ```

2. This creates `auth-integrator-enhanced.skill` file

3. Install in Claude Desktop (if applicable)

## Quick Reference: When MCP is Used

| Scenario | MCP Available? | What Happens |
|----------|---------------|--------------|
| New auth setup | ✓ | Inspects existing config, validates schema, generates accurate code |
| New auth setup | ✗ | Uses best-practice defaults, generates standard implementation |
| Add OAuth provider | ✓ | Checks available providers, gets configuration requirements |
| Add OAuth provider | ✗ | Uses documentation-based approach |
| Debug auth issues | ✓ | Validates schema, checks config consistency |
| Debug auth issues | ✗ | Uses manual verification steps |
| Schema validation | ✓ | Automated validation with detailed error messages |
| Schema validation | ✗ | Provides manual validation checklist |

## Testing Your Implementation

After Claude generates your authentication code, test it:

1. **Run the JWT test script:**
   ```bash
   cd /path/to/your/project
   export BETTER_AUTH_SECRET='your-secret-key'
   python jwt-verify-test.py
   ```

2. **Test in your app:**
   - Sign up a new user
   - Sign in and check token in browser DevTools
   - Make authenticated API request
   - Verify you only see your own data

3. **Validate with MCP** (if available):
   ```javascript
   // Claude can run this for you
   const validation = await better_auth_validate_schema({
     databaseUrl: process.env.DATABASE_URL
   })
   ```

## Troubleshooting

### "MCP server not available"
- Check Better Auth MCP is installed in Claude Code
- Verify MCP server is running
- Fall back to manual implementation

### "Schema validation failed"
- Run Better Auth migrations
- Check database connection
- Use MCP suggestions to fix schema

### "Token verification failed"
- Ensure BETTER_AUTH_SECRET matches frontend/backend
- Check token format (should be Bearer token)
- Run jwt-verify-test.py for detailed diagnostics

## Benefits of This Enhanced Version

1. **Accuracy**: Uses real config data instead of assumptions
2. **Speed**: Automated validation and code generation
3. **Safety**: Schema validation prevents runtime errors
4. **Flexibility**: Works with or without MCP
5. **Comprehensive**: Includes examples, testing, and documentation
6. **Type-Safe**: Generates TypeScript types from your schema

## Next Steps

1. **Try it out**: Use the skill in Claude Code with your project
2. **Customize**: Modify examples.md to match your patterns
3. **Extend**: Add more MCP tools as Better Auth adds features
4. **Share**: Package and share with your team

## Comparison: Old vs. Enhanced

| Feature | Original Skill | Enhanced Skill |
|---------|---------------|----------------|
| MCP Support | ✗ None | ✓ Full integration |
| Schema Validation | ✗ Manual | ✓ Automated with MCP |
| Examples | 2 basic | 6 comprehensive |
| Testing Script | ✓ Basic | ✓ Comprehensive |
| Reference Docs | ✗ None | ✓ 2 detailed guides |
| Error Handling | Basic | Detailed with MCP fallbacks |
| Type Generation | Manual | ✓ Automated with MCP |
| Config Validation | Manual | ✓ Automated with MCP |

## Additional Resources

- **Better Auth Docs**: https://better-auth.com
- **MCP Documentation**: https://modelcontextprotocol.io
- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/
- **JWT.io**: Token debugging tool

---

**Version**: 2.0  
**License**: MIT  
**Requires**: Better Auth, FastAPI, Next.js
**Optional**: Better Auth MCP Server (for enhanced features)
