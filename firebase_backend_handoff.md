# Firebase Backend Handoff Prompt for AutoSort Analytics

## Project Overview
Create a Firebase backend for AutoSort, a file organization tool that needs privacy-preserving analytics to collect anonymous data about unhandled file types from users.

## Core Requirements

### 1. Privacy-First Analytics Collection
- **Data Minimization**: Only collect file extensions (e.g., ".xyz"), never filenames, paths, or content
- **Anonymous Data**: Use anonymous user IDs, no personally identifiable information (PII)
- **Opt-in Consent**: Users must explicitly consent before any data collection
- **GDPR/CCPA Compliant**: Transparent data practices, easy opt-out

### 2. Data Structure
```typescript
interface FileTypeReport {
  extension: string;        // File extension (e.g., ".xyz")
  context: string;          // File context ("image", "document", "unknown")
  timestamp: string;        // ISO timestamp
  anonymousId: string;      // Anonymous user identifier
  version: string;          // AutoSort version
  count: number;           // Number of occurrences
}

interface UserConsent {
  userId: string;          // Anonymous user ID
  enabled: boolean;        // Consent status
  consentDate: string;     // When consent was given
  consentVersion: string;  // Version of consent form
  lastUpdated: string;     // Last update timestamp
}
```

### 3. Firebase Services Needed

#### Firestore Database
- **Collection**: `fileTypeReports`
  - Document ID: Auto-generated
  - Fields: FileTypeReport interface
  - Security: Only authenticated users can write, public read for analytics

- **Collection**: `userConsent`
  - Document ID: anonymousId
  - Fields: UserConsent interface
  - Security: User can only read/write their own consent

- **Collection**: `analyticsSummary`
  - Document ID: "current"
  - Fields: Aggregated statistics
  - Security: Public read, admin write

#### Firebase Authentication
- **Anonymous Authentication**: Allow users to authenticate anonymously
- **Custom Claims**: No special permissions needed for basic users
- **Security Rules**: Ensure users can only access their own data

#### Firebase Functions (Optional)
- **Aggregation Function**: Periodically aggregate reports into summary statistics
- **Data Cleanup**: Remove old reports to manage storage costs
- **Export Function**: Generate CSV exports for analysis

### 4. Security Rules
```javascript
// Firestore Security Rules
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // File type reports - authenticated users can write, public read
    match /fileTypeReports/{reportId} {
      allow read: if true;  // Public read for analytics
      allow write: if request.auth != null;  // Authenticated write
    }
    
    // User consent - users can only access their own data
    match /userConsent/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Analytics summary - public read, admin write
    match /analyticsSummary/{summaryId} {
      allow read: if true;  // Public read
      allow write: if request.auth != null && 
        request.auth.token.admin == true;  // Admin only
    }
  }
}
```

### 5. Client-Side Integration
```typescript
// Firebase configuration for AutoSort
const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "autosort-analytics.firebaseapp.com",
  projectId: "autosort-analytics",
  storageBucket: "autosort-analytics.appspot.com",
  messagingSenderId: "123456789",
  appId: "your-app-id"
};

// Initialize Firebase
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getAuth, signInAnonymously } from 'firebase/auth';

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);
```

### 6. API Endpoints Needed

#### Report File Type
```typescript
// POST /api/reportFileType
async function reportFileType(extension: string, context: string) {
  // 1. Check user consent
  // 2. Authenticate anonymously if needed
  // 3. Store report in Firestore
  // 4. Return success/error
}
```

#### Get Analytics Summary
```typescript
// GET /api/analyticsSummary
async function getAnalyticsSummary() {
  // 1. Return aggregated statistics
  // 2. Include top unhandled file types
  // 3. Include context breakdown
  // 4. Include version breakdown
}
```

#### Manage Consent
```typescript
// POST /api/consent
async function updateConsent(enabled: boolean) {
  // 1. Update user consent status
  // 2. Return updated consent info
}

// GET /api/consent
async function getConsentStatus() {
  // 1. Return current consent status
  // 2. Include consent date and version
}
```

### 7. Data Aggregation Strategy
- **Real-time**: Basic counts and recent reports
- **Daily**: Aggregate daily statistics
- **Weekly**: Generate weekly summaries
- **Monthly**: Create monthly analytics reports

### 8. Cost Optimization
- **Data Retention**: Keep reports for 90 days, summaries longer
- **Batch Operations**: Group multiple reports into single writes
- **Indexing**: Optimize Firestore indexes for common queries
- **Caching**: Cache frequently accessed data

### 9. Monitoring and Alerts
- **Error Tracking**: Monitor failed report submissions
- **Usage Metrics**: Track API usage and costs
- **Data Quality**: Monitor for invalid or suspicious data
- **Performance**: Monitor response times and database performance

### 10. Admin Dashboard Requirements
- **Analytics View**: Display aggregated file type reports
- **User Management**: View consent statistics
- **Data Export**: Export data to CSV/JSON
- **System Health**: Monitor Firebase services status

## Implementation Priority

### Phase 1: Core Functionality
1. Set up Firebase project with Firestore
2. Implement anonymous authentication
3. Create basic data collection endpoints
4. Set up security rules

### Phase 2: Analytics Features
1. Implement data aggregation
2. Create analytics summary endpoints
3. Add consent management
4. Build basic admin dashboard

### Phase 3: Optimization
1. Implement data retention policies
2. Add monitoring and alerts
3. Optimize for cost and performance
4. Add advanced analytics features

## Success Criteria
- ✅ Anonymous users can report unhandled file types
- ✅ Data is collected without any PII
- ✅ Users can easily opt-in/opt-out
- ✅ Analytics data is aggregated and accessible
- ✅ System is GDPR/CCPA compliant
- ✅ Costs are minimal (free tier sufficient for initial usage)
- ✅ Performance is acceptable (< 1 second response times)

## Technical Constraints
- **Budget**: Must work within Firebase free tier initially
- **Privacy**: No PII collection, anonymous data only
- **Performance**: Sub-second response times
- **Scalability**: Handle 1000+ users reporting data
- **Compliance**: GDPR/CCPA compliant by design

## Additional Context
- This is for AutoSort, a Python-based file organization tool
- Users will be reporting file extensions they encounter that aren't supported
- The goal is to identify which file types to add support for next
- Data should be publicly accessible for transparency
- The system should be simple to maintain and scale

Please scaffold a complete Firebase backend that meets these requirements, including:
1. Firebase project setup instructions
2. Firestore database schema
3. Security rules
4. Cloud Functions (if needed)
5. Client-side integration code
6. Admin dashboard (basic)
7. Deployment instructions
8. Testing procedures
