#!/usr/bin/env python3
"""
Firebase Analytics Client for AutoSort

This module provides a Python client for connecting AutoSort to Firebase
for privacy-preserving analytics collection.

Requirements:
- firebase-admin package
- Firebase project with Firestore enabled
- Service account key (for server-side) or web config (for client-side)

Usage:
    from firebase_analytics import FirebaseAnalyticsClient
    
    client = FirebaseAnalyticsClient()
    client.report_file_type(".xyz", "image")
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, auth
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    logging.warning("Firebase Admin SDK not installed. Install with: pip install firebase-admin")

logger = logging.getLogger(__name__)


class FirebaseAnalyticsClient:
    """
    Firebase client for AutoSort analytics.
    
    Handles anonymous authentication, data collection, and consent management
    using Firebase Firestore and Authentication.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize Firebase client.
        
        Args:
            config_path: Path to Firebase service account key or config
        """
        if not FIREBASE_AVAILABLE:
            raise ImportError("Firebase Admin SDK not available. Install with: pip install firebase-admin")
        
        self.db = None
        self.anonymous_user = None
        self.consent_enabled = False
        
        # Initialize Firebase
        self._initialize_firebase(config_path)
    
    def _initialize_firebase(self, config_path: Optional[Path] = None):
        """Initialize Firebase Admin SDK."""
        try:
            if config_path and config_path.exists():
                # Use service account key
                cred = credentials.Certificate(str(config_path))
                firebase_admin.initialize_app(cred)
            else:
                # Use default credentials (for local development)
                firebase_admin.initialize_app()
            
            self.db = firestore.client()
            logger.info("Firebase initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    def authenticate_anonymously(self) -> bool:
        """
        Authenticate user anonymously.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # For client-side, you'd use Firebase Auth SDK
            # For server-side, we'll use a simple anonymous ID
            self.anonymous_user = self._generate_anonymous_id()
            logger.info(f"Authenticated anonymously: {self.anonymous_user[:8]}...")
            return True
            
        except Exception as e:
            logger.error(f"Anonymous authentication failed: {e}")
            return False
    
    def _generate_anonymous_id(self) -> str:
        """Generate anonymous user ID."""
        import hashlib
        import platform
        import uuid
        
        # Create stable anonymous ID based on system info
        system_info = f"{platform.system()}{platform.machine()}{uuid.getnode()}"
        return hashlib.sha256(system_info.encode()).hexdigest()[:16]
    
    def check_consent_status(self) -> Dict[str, Any]:
        """
        Check user consent status.
        
        Returns:
            Consent status dictionary
        """
        if not self.anonymous_user:
            return {"enabled": False, "error": "Not authenticated"}
        
        try:
            doc_ref = self.db.collection('userConsent').document(self.anonymous_user)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                self.consent_enabled = data.get('enabled', False)
                return {
                    "enabled": self.consent_enabled,
                    "consent_date": data.get('consentDate', ''),
                    "version": data.get('version', ''),
                    "last_updated": data.get('lastUpdated', '')
                }
            else:
                # No consent record found
                self.consent_enabled = False
                return {"enabled": False, "consent_date": "", "version": ""}
                
        except Exception as e:
            logger.error(f"Failed to check consent status: {e}")
            return {"enabled": False, "error": str(e)}
    
    def update_consent(self, enabled: bool) -> bool:
        """
        Update user consent status.
        
        Args:
            enabled: Whether to enable analytics
            
        Returns:
            True if update successful, False otherwise
        """
        if not self.anonymous_user:
            logger.error("Not authenticated")
            return False
        
        try:
            consent_data = {
                'anonymousId': self.anonymous_user,
                'enabled': enabled,
                'consentDate': datetime.now().isoformat(),
                'version': '1.0',
                'lastUpdated': datetime.now().isoformat()
            }
            
            doc_ref = self.db.collection('userConsent').document(self.anonymous_user)
            doc_ref.set(consent_data)
            
            self.consent_enabled = enabled
            logger.info(f"Consent updated: {enabled}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update consent: {e}")
            return False
    
    def report_file_type(self, extension: str, context: str = "unknown", 
                        version: str = "2.3") -> bool:
        """
        Report an unhandled file type.
        
        Args:
            extension: File extension (e.g., ".xyz")
            context: File context (e.g., "image", "document")
            version: AutoSort version
            
        Returns:
            True if report successful, False otherwise
        """
        if not self.consent_enabled:
            logger.debug("Analytics disabled - not reporting file type")
            return False
        
        if not self.anonymous_user:
            logger.error("Not authenticated")
            return False
        
        try:
            # Normalize extension
            extension = extension.lower().strip()
            if not extension.startswith('.'):
                extension = f".{extension}"
            
            report_data = {
                'extension': extension,
                'context': context,
                'timestamp': datetime.now().isoformat(),
                'anonymousId': self.anonymous_user,
                'version': version,
                'count': 1
            }
            
            # Add to Firestore
            doc_ref = self.db.collection('fileTypeReports').document()
            doc_ref.set(report_data)
            
            logger.debug(f"Reported file type: {extension} ({context})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to report file type: {e}")
            return False
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """
        Get analytics summary data.
        
        Returns:
            Summary statistics dictionary
        """
        try:
            # Get summary from Firestore
            doc_ref = self.db.collection('analyticsSummary').document('current')
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            else:
                # Generate basic summary from reports
                return self._generate_basic_summary()
                
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {"error": str(e)}
    
    def _generate_basic_summary(self) -> Dict[str, Any]:
        """Generate basic summary from recent reports."""
        try:
            # Get recent reports (last 30 days)
            thirty_days_ago = datetime.now().timestamp() - (30 * 24 * 60 * 60)
            
            reports_ref = self.db.collection('fileTypeReports')
            reports = reports_ref.where('timestamp', '>=', 
                                      datetime.fromtimestamp(thirty_days_ago).isoformat()).get()
            
            # Analyze reports
            extensions = []
            contexts = []
            versions = []
            
            for report in reports:
                data = report.to_dict()
                extensions.append(data.get('extension', ''))
                contexts.append(data.get('context', ''))
                versions.append(data.get('version', ''))
            
            # Count occurrences
            from collections import Counter
            extension_counts = Counter(extensions)
            context_counts = Counter(contexts)
            version_counts = Counter(versions)
            
            return {
                'total_reports': len(reports),
                'unique_extensions': len(extension_counts),
                'top_extensions': extension_counts.most_common(10),
                'context_breakdown': dict(context_counts),
                'version_breakdown': dict(version_counts),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate basic summary: {e}")
            return {"error": str(e)}
    
    def export_data(self, output_file: str, days: int = 30) -> bool:
        """
        Export analytics data to JSON file.
        
        Args:
            output_file: Output file path
            days: Number of days to export
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            # Get reports from specified time period
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            reports_ref = self.db.collection('fileTypeReports')
            reports = reports_ref.where('timestamp', '>=', 
                                      datetime.fromtimestamp(cutoff_date).isoformat()).get()
            
            # Convert to list of dictionaries
            data = []
            for report in reports:
                data.append(report.to_dict())
            
            # Write to file
            with open(output_file, 'w') as f:
                json.dump({
                    'export_date': datetime.now().isoformat(),
                    'days_exported': days,
                    'total_reports': len(data),
                    'reports': data
                }, f, indent=2)
            
            logger.info(f"Exported {len(data)} reports to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return False


# Integration with AutoSort analytics system
def integrate_with_autosort_analytics():
    """
    Integration function to connect Firebase with AutoSort's analytics system.
    """
    try:
        # Initialize Firebase client
        client = FirebaseAnalyticsClient()
        
        # Authenticate anonymously
        if not client.authenticate_anonymously():
            logger.error("Failed to authenticate with Firebase")
            return None
        
        # Check consent status
        consent_status = client.check_consent_status()
        if not consent_status.get('enabled', False):
            logger.info("User has not consented to Firebase analytics")
            return None
        
        return client
        
    except Exception as e:
        logger.error(f"Failed to integrate with Firebase: {e}")
        return None


# Example usage
if __name__ == "__main__":
    # Test the Firebase client
    try:
        client = FirebaseAnalyticsClient()
        
        # Authenticate
        if client.authenticate_anonymously():
            print("✅ Authenticated anonymously")
            
            # Check consent
            consent = client.check_consent_status()
            print(f"Consent status: {consent}")
            
            # Update consent (for testing)
            if client.update_consent(True):
                print("✅ Consent updated")
                
                # Report a test file type
                if client.report_file_type(".test", "unknown"):
                    print("✅ File type reported")
                
                # Get summary
                summary = client.get_analytics_summary()
                print(f"Analytics summary: {summary}")
            
        else:
            print("❌ Authentication failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
