"""
File Organizer for AutoSort

Handles the core file organization logic with improved error handling,
progress tracking, and undo functionality.
"""

import logging
import shutil
import os
import fnmatch
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import time

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Operation type enumeration."""
    MOVE = "move"
    CREATE_DIR = "create_dir"
    DELETE = "delete"


@dataclass
class FileOperation:
    """File operation record for undo functionality."""
    operation_type: OperationType
    source: Path
    destination: Optional[Path] = None
    timestamp: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class FileInfo:
    """File information structure."""
    path: Path
    size: int
    category: str
    subcategory: str = ""
    error_message: str = ""


@dataclass
class OrganizationResult:
    """Organization operation result."""
    success: bool
    files_processed: int
    files_moved: int
    errors: int
    operations: List[FileOperation]
    error_log: List[str]


class FileOrganizer:
    """
    Handles file organization with improved error handling and progress tracking.
    
    This class manages the core file organization logic, including file scanning,
    categorization, moving, and undo functionality.
    """
    
    def __init__(self, config_manager, path_manager, undo_manager=None):
        """
        Initialize the file organizer.
        
        Args:
            config_manager: Configuration manager instance
            path_manager: Path manager instance
            undo_manager: Undo manager instance (optional)
        """
        self.config_manager = config_manager
        self.path_manager = path_manager
        self.undo_manager = undo_manager
        self.ignore_patterns: List[str] = []
        self.progress_callback: Optional[Callable[[int, int, str], None]] = None
        self.current_transaction_id: Optional[str] = None
        
    def set_progress_callback(self, callback: Callable[[int, int, str], None]) -> None:
        """
        Set progress callback function.
        
        Args:
            callback: Function to call with progress updates
        """
        self.progress_callback = callback
    
    def set_current_transaction(self, transaction_id: str) -> None:
        """
        Set the current transaction ID for tracking operations.
        
        Args:
            transaction_id: Current transaction ID
        """
        self.current_transaction_id = transaction_id
    
    def _add_operation_to_transaction(self, operation: FileOperation) -> None:
        """
        Add an operation to the current transaction if available.
        
        Args:
            operation: File operation to add
        """
        if self.undo_manager and self.current_transaction_id:
            self.undo_manager.add_operation(self.current_transaction_id, operation)
    
    def load_ignore_patterns(self, ignore_file: Path) -> bool:
        """
        Load ignore patterns from file.
        
        Args:
            ignore_file: Path to ignore file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            if not ignore_file.exists():
                logger.debug(f"Ignore file not found: {ignore_file}")
                return True
            
            with open(ignore_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.ignore_patterns = []
            for line in content.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    self.ignore_patterns.append(line)
            
            logger.info(f"Loaded {len(self.ignore_patterns)} ignore patterns")
            return True
            
        except Exception as e:
            logger.error(f"Error loading ignore patterns: {e}")
            return False
    
    def organize_directory(self, source_path: Path, dry_run: bool = False) -> OrganizationResult:
        """
        Organize files in a directory.
        
        Args:
            source_path: Source directory path
            dry_run: If True, don't actually move files
            
        Returns:
            OrganizationResult with operation details
        """
        try:
            # Validate source path
            path_info = self.path_manager.validate_path(source_path)
            if not path_info.exists or not path_info.is_directory:
                return OrganizationResult(
                    success=False,
                    files_processed=0,
                    files_moved=0,
                    errors=1,
                    operations=[],
                    error_log=[f"Invalid source path: {path_info.error_message}"]
                )
            
            # Get target path
            target_path = self.path_manager.get_target_path(source_path)
            
            # Scan files
            files_to_process = self._scan_files(source_path)
            if not files_to_process:
                return OrganizationResult(
                    success=True,
                    files_processed=0,
                    files_moved=0,
                    errors=0,
                    operations=[],
                    error_log=[]
                )
            
            logger.info(f"Found {len(files_to_process)} files to organize")
            
            # Process files
            return self._process_files(files_to_process, target_path, dry_run)
            
        except Exception as e:
            logger.error(f"Error organizing directory: {e}")
            return OrganizationResult(
                success=False,
                files_processed=0,
                files_moved=0,
                errors=1,
                operations=[],
                error_log=[f"Unexpected error: {e}"]
            )
    
    def analyze_files(self, source_path: Path) -> Dict[str, Any]:
        """
        Analyze files in a directory without moving them.
        
        Args:
            source_path: Source directory path
            
        Returns:
            Analysis results
        """
        try:
            files_to_process = self._scan_files(source_path)
            
            # Categorize files
            category_stats = {}
            total_size = 0
            
            for file_path in files_to_process:
                category, subcategory = self._categorize_file(file_path)
                size = file_path.stat().st_size
                
                if category not in category_stats:
                    category_stats[category] = {
                        'count': 0,
                        'size': 0,
                        'subcategories': {}
                    }
                
                category_stats[category]['count'] += 1
                category_stats[category]['size'] += size
                total_size += size
                
                if subcategory:
                    if subcategory not in category_stats[category]['subcategories']:
                        category_stats[category]['subcategories'][subcategory] = {
                            'count': 0,
                            'size': 0
                        }
                    category_stats[category]['subcategories'][subcategory]['count'] += 1
                    category_stats[category]['subcategories'][subcategory]['size'] += size
            
            return {
                'total_files': len(files_to_process),
                'total_size': total_size,
                'categories': category_stats
            }
            
        except Exception as e:
            logger.error(f"Error analyzing files: {e}")
            return {
                'total_files': 0,
                'total_size': 0,
                'categories': {},
                'error': str(e)
            }
    
    def _scan_files(self, source_path: Path) -> List[Path]:
        """
        Scan directory for files to organize.
        
        Args:
            source_path: Source directory path
            
        Returns:
            List of file paths to process
        """
        files_to_process = []
        
        try:
            for item in source_path.iterdir():
                if not item.is_file():
                    continue
                
                # Skip system files and script files
                if self._should_skip_file(item):
                    continue
                
                # Check ignore patterns
                if self._should_ignore_file(item):
                    continue
                
                files_to_process.append(item)
                
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
        
        return files_to_process
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """
        Check if a file should be skipped.
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file should be skipped
        """
        skip_patterns = [
            '.DS_Store',
            'Thumbs.db',
            'desktop.ini',
            'autosort.py',
            'autosort_config.json',
            'autosort_gui.py',
            '.sortignore'
        ]
        
        return file_path.name in skip_patterns
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """
        Check if a file should be ignored based on patterns.
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file should be ignored
        """
        try:
            return any(fnmatch.fnmatch(file_path.name, pattern) for pattern in self.ignore_patterns)
        except Exception:
            return False
    
    def _categorize_file(self, file_path: Path) -> Tuple[str, str]:
        """
        Categorize a file based on its extension and metadata.
        
        Args:
            file_path: File path to categorize
            
        Returns:
            Tuple of (category, subcategory)
        """
        extension = file_path.suffix.lower()
        extension_map = self.config_manager.get_extension_mapping()
        
        # Get main category
        category = extension_map.get(extension, "Miscellaneous")
        
        # Get subcategory using configuration-based system
        subcategory = self._categorize_subcategory(file_path, category)
        
        return category, subcategory
    
    def _categorize_subcategory(self, file_path: Path, category: str) -> str:
        """
        Categorize a file into a subcategory based on configuration.
        
        Args:
            file_path: File path to categorize
            category: Main category name
            
        Returns:
            Subcategory name or empty string if no subcategory
        """
        try:
            # Get category configuration
            categories = self.config_manager.get_categories()
            if category not in categories:
                return ""
            
            category_config = categories[category]
            if not hasattr(category_config, 'subcategories') or not category_config.subcategories:
                return ""
            
            # Check subcategories in priority order: extensions -> patterns -> exif
            for subcategory_name, subcategory_config in category_config.subcategories.items():
                if self._matches_subcategory(file_path, subcategory_config):
                    return subcategory_config.folder_name
            
            return ""
            
        except Exception as e:
            logger.debug(f"Error categorizing subcategory for {file_path}: {e}")
            return ""
    
    def _matches_subcategory(self, file_path: Path, subcategory_config) -> bool:
        """
        Check if a file matches a subcategory configuration.
        
        Args:
            file_path: File path to check
            subcategory_config: Subcategory configuration object
            
        Returns:
            True if file matches subcategory
        """
        # Check extensions first (highest priority)
        if hasattr(subcategory_config, 'extensions') and subcategory_config.extensions:
            if file_path.suffix.lower() in [ext.lower() for ext in subcategory_config.extensions]:
                return True
        
        # Check patterns second
        if hasattr(subcategory_config, 'patterns') and subcategory_config.patterns:
            for pattern in subcategory_config.patterns:
                if self._matches_pattern(file_path.name, pattern):
                    return True
        
        # Check EXIF indicators third (only for images)
        if hasattr(subcategory_config, 'exif_indicators') and subcategory_config.exif_indicators:
            if self._matches_exif_indicators(file_path, subcategory_config.exif_indicators):
                return True
        
        return False
    
    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """
        Check if filename matches a pattern with wildcards.
        
        Args:
            filename: Filename to check
            pattern: Pattern with * wildcards
            
        Returns:
            True if filename matches pattern
        """
        import fnmatch
        return fnmatch.fnmatch(filename.lower(), pattern.lower())
    
    def _matches_exif_indicators(self, file_path: Path, exif_indicators: List[str]) -> bool:
        """
        Check if file matches EXIF indicators.
        
        Args:
            file_path: File path to check
            exif_indicators: List of EXIF indicators to check for
            
        Returns:
            True if file matches any EXIF indicator
        """
        try:
            # Only check EXIF for image files
            image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.webp']
            if file_path.suffix.lower() not in image_extensions:
                return False
            
            metadata = self._analyze_image_metadata(file_path)
            
            # Check software used
            if metadata.get('software_used'):
                for indicator in exif_indicators:
                    if indicator.lower() in metadata['software_used'].lower():
                        return True
            
            # Check camera info
            if metadata.get('camera_info'):
                for indicator in exif_indicators:
                    if indicator.lower() in metadata['camera_info'].lower():
                        return True
            
            return False
            
        except Exception as e:
            logger.debug(f"Error checking EXIF indicators for {file_path}: {e}")
            return False
    
    def _categorize_image_subfolder(self, file_path: Path) -> str:
        """
        Categorize image into subfolder based on metadata.
        
        Args:
            file_path: Image file path
            
        Returns:
            Subcategory name
        """
        try:
            # Check for design files first
            design_extensions = ['.psd', '.ai', '.eps', '.sketch', '.fig']
            if file_path.suffix.lower() in design_extensions:
                return "Design Files"
            
            # Check for RAW photos
            raw_extensions = ['.raw', '.dng', '.cr2', '.nef', '.arw', '.orf']
            if file_path.suffix.lower() in raw_extensions:
                return "RAW Photos"
            
            # Check for screenshots
            if self._is_screenshot(file_path):
                return "Screenshots"
            
            # Check metadata for other categorizations
            metadata = self._analyze_image_metadata(file_path)
            
            if metadata.get('software_used'):
                adobe_software = ['Adobe Photoshop', 'Adobe Lightroom', 'Adobe Camera Raw']
                if any(software.lower() in metadata['software_used'].lower() for software in adobe_software):
                    return "Adobe Edited"
            
            if metadata.get('camera_info'):
                return "Camera Photos"
            
            # Check for web downloads
            web_patterns = [r'^image\d*\.', r'^img\d*\.', r'^photo\d*\.']
            for pattern in web_patterns:
                if re.match(pattern, file_path.name, re.IGNORECASE):
                    return "Web Downloads"
            
            return "General"
            
        except Exception as e:
            logger.debug(f"Error categorizing image {file_path}: {e}")
            return "General"
    
    def _is_screenshot(self, file_path: Path) -> bool:
        """
        Check if an image is likely a screenshot.
        
        Args:
            file_path: Image file path
            
        Returns:
            True if likely a screenshot
        """
        screenshot_patterns = [
            r'Screenshot.*\.(png|jpg|jpeg)$',
            r'Screen Shot.*\.(png|jpg|jpeg)$'
        ]
        
        for pattern in screenshot_patterns:
            if re.match(pattern, file_path.name, re.IGNORECASE):
                return True
        
        return False
    
    def _analyze_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze image metadata for categorization.
        
        Args:
            file_path: Image file path
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'software_used': None,
            'camera_info': None,
            'creation_date': None
        }
        
        try:
            import PIL.Image
            import PIL.ExifTags
            
            with PIL.Image.open(file_path) as img:
                exif = img._getexif()
                if exif:
                    # Software tag
                    software = exif.get(305)
                    if software:
                        metadata['software_used'] = software
                    
                    # Camera info
                    make = exif.get(271)
                    model = exif.get(272)
                    if make or model:
                        metadata['camera_info'] = f"{make} {model}".strip()
                    
                    # Creation date
                    date_original = exif.get(36867)
                    if date_original:
                        metadata['creation_date'] = date_original
                        
        except ImportError:
            logger.debug("Pillow not available for image metadata analysis")
        except Exception as e:
            logger.debug(f"Error analyzing image metadata: {e}")
        
        return metadata
    
    def _process_files(self, files: List[Path], target_path: Path, dry_run: bool) -> OrganizationResult:
        """
        Process files for organization.
        
        Args:
            files: List of files to process
            target_path: Target directory path
            dry_run: If True, don't actually move files
            
        Returns:
            OrganizationResult with operation details
        """
        operations = []
        error_log = []
        files_moved = 0
        errors = 0
        
        for i, file_path in enumerate(files):
            try:
                # Update progress
                if self.progress_callback:
                    self.progress_callback(i + 1, len(files), f"Processing {file_path.name}")
                
                # Categorize file
                category, subcategory = self._categorize_file(file_path)
                
                # Determine destination
                if subcategory:
                    dest_dir = target_path / category / subcategory
                else:
                    dest_dir = target_path / category
                
                # Create directory if needed
                if not dry_run:
                    if not self.path_manager.ensure_directory(dest_dir):
                        error_log.append(f"Failed to create directory: {dest_dir}")
                        errors += 1
                        continue
                
                # Generate unique destination path
                dest_file = self._get_unique_path(dest_dir / file_path.name)
                
                # Create operation record
                operation = FileOperation(
                    operation_type=OperationType.MOVE,
                    source=file_path,
                    destination=dest_file
                )
                
                if dry_run:
                    # Add operation for preview
                    operations.append(operation)
                    logger.info(f"Would move: {file_path.name} → {dest_file}")
                else:
                    # Move file
                    if self._safe_move_file(file_path, dest_file):
                        operations.append(operation)
                        # Add to undo transaction
                        self._add_operation_to_transaction(operation)
                        files_moved += 1
                        logger.info(f"Moved: {file_path.name} → {dest_file}")
                    else:
                        error_log.append(f"Failed to move: {file_path.name}")
                        errors += 1
                
            except Exception as e:
                error_log.append(f"Error processing {file_path.name}: {e}")
                errors += 1
                logger.error(f"Error processing {file_path}: {e}")
        
        return OrganizationResult(
            success=errors == 0,
            files_processed=len(files),
            files_moved=files_moved,
            errors=errors,
            operations=operations,
            error_log=error_log
        )
    
    def _get_unique_path(self, dest_path: Path) -> Path:
        """
        Generate a unique path for the destination file.
        
        Args:
            dest_path: Original destination path
            
        Returns:
            Unique destination path
        """
        if not dest_path.exists():
            return dest_path
        
        stem = dest_path.stem
        suffix = dest_path.suffix
        parent = dest_path.parent
        
        counter = 1
        while counter <= 1000:
            candidate = parent / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1
        
        # If we've tried 1000 times, append timestamp
        timestamp = int(time.time())
        return parent / f"{stem}_{timestamp}{suffix}"
    
    def _safe_move_file(self, source: Path, dest: Path) -> bool:
        """
        Safely move a file with error handling.
        
        Args:
            source: Source file path
            dest: Destination file path
            
        Returns:
            True if moved successfully, False otherwise
        """
        try:
            # Check source
            if not source.exists():
                logger.error(f"Source file does not exist: {source}")
                return False
            
            if not source.is_file():
                logger.error(f"Source is not a file: {source}")
                return False
            
            # Check permissions
            if not os.access(source, os.R_OK):
                logger.error(f"No read permission for: {source}")
                return False
            
            if not os.access(dest.parent, os.W_OK):
                logger.error(f"No write permission for destination directory: {dest.parent}")
                return False
            
            # Perform move
            shutil.move(str(source), str(dest))
            return True
            
        except Exception as e:
            logger.error(f"Error moving {source} to {dest}: {e}")
            return False
