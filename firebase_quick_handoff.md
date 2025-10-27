# Firebase Studio App Handoff - AutoSort Analytics Backend

## Quick Setup Prompt for Firebase LLM Assistant

**Project**: AutoSort Analytics Backend
**Purpose**: Collect anonymous file type usage data from AutoSort users

### What I Need:
Create a Firebase backend for privacy-preserving analytics that collects anonymous data about unhandled file types.

### Core Data Structure:
```typescript
// File type reports (anonymous)
{
  extension: ".xyz",           // File extension only
  context: "image",            // File context
  timestamp: "2025-01-27T...", // When reported
  anonymousId: "abc123",       // Anonymous user ID
  version: "2.3",             // App version
  count: 1                    // Occurrence count
}

// User consent tracking
{
  anonymousId: "abc123",
  enabled: true,
  consentDate: "2025-01-27T...",
  version: "1.0"
}
```

### Required Features:
1. **Anonymous Authentication** - Users sign in anonymously
2. **File Type Reporting** - Submit unhandled file extensions
3. **Consent Management** - Opt-in/opt-out system
4. **Analytics Dashboard** - View aggregated data
5. **Data Export** - Export to CSV/JSON

### Firebase Services:
- **Firestore** - Store reports and consent data
- **Authentication** - Anonymous auth only
- **Security Rules** - Public read, authenticated write
- **Cloud Functions** - Data aggregation (optional)

### Privacy Requirements:
- No PII collection
- Anonymous data only
- GDPR/CCPA compliant
- Easy opt-out

### Success Criteria:
- Anonymous users can report file types
- Data is aggregated and viewable
- Users can manage consent
- System is cost-effective (free tier)

**Please scaffold a complete Firebase backend with:**
1. Firestore database schema
2. Security rules
3. Authentication setup
4. Basic API endpoints
5. Admin dashboard
6. Client integration code
7. Deployment instructions

**Focus on simplicity and privacy-first design.**
