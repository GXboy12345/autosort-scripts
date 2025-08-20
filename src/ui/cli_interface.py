"""
Command Line Interface for AutoSort

Provides a modern, accessible command-line interface with improved
user experience, better menu design, and keyboard shortcuts.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

from core.config_manager import ConfigManager
from core.file_organizer import FileOrganizer
from core.path_manager import PathManager
from utils.undo_manager import UndoManager

from utils.logger import ProgressLogger

logger = logging.getLogger(__name__)


class MenuOption(Enum):
    """Menu option enumeration."""
    ORGANIZE_DESKTOP = "organize_desktop"
    ORGANIZE_DOWNLOADS = "organize_downloads"
    ORGANIZE_CUSTOM = "organize_custom"
    PREVIEW_DESKTOP = "preview_desktop"
    PREVIEW_DOWNLOADS = "preview_downloads"
    PREVIEW_CUSTOM = "preview_custom"
    CONFIG_WIZARD = "config_wizard"
    UNDO_LAST = "undo_last"

    HELP = "help"
    EXIT = "exit"


@dataclass
class MenuItem:
    """Menu item structure."""
    option: MenuOption
    key: str
    title: str
    description: str
    shortcut: Optional[str] = None


class CLIInterface:
    """
    Modern command-line interface for AutoSort.
    
    This class provides a user-friendly CLI with improved navigation,
    accessibility features, and better visual design.
    """
    
    def __init__(self, config_manager: ConfigManager, file_organizer: FileOrganizer,
                 undo_manager: UndoManager):
        """
        Initialize the CLI interface.
        
        Args:
            config_manager: Configuration manager instance
            file_organizer: File organizer instance
            undo_manager: Undo manager instance
        """
        self.config_manager = config_manager
        self.file_organizer = file_organizer
        self.undo_manager = undo_manager
        self.path_manager = PathManager()
        
        # Connect file organizer to undo manager
        if hasattr(self.file_organizer, 'undo_manager'):
            self.file_organizer.undo_manager = self.undo_manager
        
        self.progress_logger = ProgressLogger(logger)
        self.current_menu = "main"
        self.menu_stack = []
        
        self._setup_menu_items()
    
    def run(self) -> int:
        """
        Run the CLI interface.
        
        Returns:
            Exit code
        """
        try:
            self._show_welcome()
            self._show_main_menu()
            return 0
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            return 0
        except Exception as e:
            logger.error(f"CLI error: {e}")
            return 1
    

    
    def _setup_menu_items(self) -> None:
        """Set up menu items."""
        self.menu_items = {
            MenuOption.ORGANIZE_DESKTOP: MenuItem(
                option=MenuOption.ORGANIZE_DESKTOP,
                key="1",
                title="Organize Desktop",
                description="Sort files from your Desktop folder"
            ),
            MenuOption.ORGANIZE_DOWNLOADS: MenuItem(
                option=MenuOption.ORGANIZE_DOWNLOADS,
                key="2",
                title="Organize Downloads",
                description="Sort files from your Downloads folder"
            ),
            MenuOption.ORGANIZE_CUSTOM: MenuItem(
                option=MenuOption.ORGANIZE_CUSTOM,
                key="3",
                title="Organize Custom Folder",
                description="Choose any folder to organize"
            ),
            MenuOption.PREVIEW_DESKTOP: MenuItem(
                option=MenuOption.PREVIEW_DESKTOP,
                key="4",
                title="Preview Desktop Organization",
                description="See what would happen without moving files"
            ),
            MenuOption.PREVIEW_DOWNLOADS: MenuItem(
                option=MenuOption.PREVIEW_DOWNLOADS,
                key="5",
                title="Preview Downloads Organization",
                description="See what would happen without moving files"
            ),
            MenuOption.PREVIEW_CUSTOM: MenuItem(
                option=MenuOption.PREVIEW_CUSTOM,
                key="6",
                title="Preview Custom Folder Organization",
                description="See what would happen without moving files"
            ),
            MenuOption.CONFIG_WIZARD: MenuItem(
                option=MenuOption.CONFIG_WIZARD,
                key="7",
                title="Configuration Wizard",
                description="Customize categories and settings"
            ),
            MenuOption.UNDO_LAST: MenuItem(
                option=MenuOption.UNDO_LAST,
                key="8",
                title="Undo Last Operation",
                description="Revert the last file organization"
            ),
            MenuOption.EXIT: MenuItem(
                option=MenuOption.EXIT,
                key="q",
                title="Exit",
                description="Quit the application"
            )
        }
    
    def _show_welcome(self) -> None:
        """Show welcome message."""
        print("\n" + "=" * 60)
        print("🎯 AutoSort - File Organizer")
        print("=" * 60)
        print("Organize your files automatically with improved user experience")
        print("and modern interface features.")
        print()
        
        # Show configuration status
        status_info = self.config_manager.get_status_info()
        print(f"📋 Configuration: {status_info['status']} (v{status_info['version']})")
        print(f"📁 Categories: {status_info['categories_count']}")
        
        # Show undo info
        undo_info = self.undo_manager.get_undo_info()
        if undo_info['can_undo']:
            print(f"↩️  Can undo: {undo_info['last_transaction']}")
        

        
        print("=" * 60)
        print()
    
    def _show_main_menu(self) -> None:
        """Show the main menu."""
        while True:
            self._display_menu("Main Menu", [
                MenuOption.ORGANIZE_DESKTOP,
                MenuOption.ORGANIZE_DOWNLOADS,
                MenuOption.ORGANIZE_CUSTOM,
                MenuOption.PREVIEW_DESKTOP,
                MenuOption.PREVIEW_DOWNLOADS,
                MenuOption.PREVIEW_CUSTOM,
                MenuOption.CONFIG_WIZARD,
                MenuOption.UNDO_LAST,
                MenuOption.EXIT
            ])
            
            choice = self._get_user_choice()
            if not self._handle_menu_choice(choice):
                break
    
    def _display_menu(self, title: str, options: list) -> None:
        """
        Display a menu with options.
        
        Args:
            title: Menu title
            options: List of menu options
        """
        print(f"\n📋 {title}")
        print("-" * 40)
        
        for option in options:
            if option in self.menu_items:
                item = self.menu_items[option]
                print(f"{item.key}. {item.title}")
                print(f"   {item.description}")
                print()
        
        print("Enter your choice:")
    
    def _get_user_choice(self) -> str:
        """
        Get user choice from input.
        
        Returns:
            User's choice
        """
        try:
            choice = input("> ").strip().lower()
            return choice
        except EOFError:
            return "q"
    
    def _handle_menu_choice(self, choice: str) -> bool:
        """
        Handle user menu choice.
        
        Args:
            choice: User's choice
            
        Returns:
            True to continue, False to exit
        """
        # Handle menu options
        for option, item in self.menu_items.items():
            if choice == item.key:
                return self._execute_menu_option(option)
        
        # Handle special commands
        if choice == "q" or choice == "quit":
            return False
        else:
            print(f"❌ Invalid choice: {choice}")
            print("Type 'q' to quit.")
            return True
    
    def _execute_menu_option(self, option: MenuOption) -> bool:
        """
        Execute a menu option.
        
        Args:
            option: Menu option to execute
            
        Returns:
            True to continue, False to exit
        """
        try:
            if option == MenuOption.ORGANIZE_DESKTOP:
                self._organize_directory(self.path_manager.get_desktop_path())
            elif option == MenuOption.ORGANIZE_DOWNLOADS:
                self._organize_directory(self.path_manager.get_downloads_path())
            elif option == MenuOption.ORGANIZE_CUSTOM:
                self._select_custom_folder()
            elif option == MenuOption.PREVIEW_DESKTOP:
                self._organize_directory(self.path_manager.get_desktop_path(), dry_run=True)
            elif option == MenuOption.PREVIEW_DOWNLOADS:
                self._organize_directory(self.path_manager.get_downloads_path(), dry_run=True)
            elif option == MenuOption.PREVIEW_CUSTOM:
                self._organize_directory(None, dry_run=True)
            elif option == MenuOption.CONFIG_WIZARD:
                self._show_config_wizard()
            elif option == MenuOption.UNDO_LAST:
                self._undo_last_operation()
            elif option == MenuOption.EXIT:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing menu option {option}: {e}")
            print(f"❌ Error: {e}")
            return True
    
    def _organize_directory(self, source_path: Optional[Path], dry_run: bool = False) -> None:
        """
        Organize files in a directory.
        
        Args:
            source_path: Source directory path (None for custom selection)
            dry_run: If True, don't actually move files
        """
        try:
            # Get source path if not provided
            if source_path is None:
                source_path = self._select_custom_folder()
                if source_path is None:
                    return
            
            # Validate path
            path_info = self.path_manager.validate_path(source_path)
            if not path_info.exists or not path_info.is_directory:
                print(f"❌ Invalid directory: {source_path}")
                return
            
            # Load ignore patterns
            ignore_file = Path(".sortignore")
            self.file_organizer.load_ignore_patterns(ignore_file)
            
            # Set up progress callback
            def progress_callback(current: int, total: int, message: str):
                percentage = (current / total) * 100 if total > 0 else 0
                print(f"\r📊 Progress: {percentage:.1f}% ({current}/{total}) - {message}", end="", flush=True)
            
            self.file_organizer.set_progress_callback(progress_callback)
            
            # Start undo transaction if not dry run
            transaction_id = None
            if not dry_run:
                description = f"Organize {source_path.name}"
                transaction_id = self.undo_manager.start_transaction(description)
                # Set current transaction in file organizer
                self.file_organizer.set_current_transaction(transaction_id)
            
            # Organize files
            mode = "Preview" if dry_run else "Organize"
            print(f"\n🔄 {mode}ing files in: {source_path}")
            
            result = self.file_organizer.organize_directory(source_path, dry_run)
            
            print()  # New line after progress
            
            # Show results
            self._show_organization_results(result, dry_run)
            
            # Commit transaction if successful
            if not dry_run and transaction_id and result.success:
                self.undo_manager.commit_transaction(transaction_id)
                print("✅ Transaction saved for undo")
            
        except Exception as e:
            logger.error(f"Error organizing directory: {e}")
            print(f"❌ Error: {e}")
    
    def _select_custom_folder(self) -> Optional[Path]:
        """
        Select a custom folder for organization.
        
        Returns:
            Selected folder path or None if cancelled
        """
        print("📁 Opening folder selection dialog...")
        selected_path = self.path_manager.select_folder_dialog()
        
        if selected_path:
            print(f"✅ Selected: {selected_path}")
            return selected_path
        else:
            print("❌ No folder selected")
            return None
    
    def _show_organization_results(self, result: Any, dry_run: bool) -> None:
        """
        Show organization results.
        
        Args:
            result: Organization result
            dry_run: Whether this was a dry run
        """
        if dry_run:
            print(f"\n📋 Preview Summary:")
            print(f"   Files that would be organized: {result.files_processed}")
            print(f"   Categories: {len([op for op in result.operations])}")
            
            # Show file analysis
            if result.files_processed > 0:
                self._show_file_analysis(result)
            
            # Show detailed preview of what would happen
            if result.operations:
                print(f"\n📄 Files that would be moved:")
                for op in result.operations:
                    if op.operation_type.value == "move":
                        source_name = op.source.name
                        dest_path = op.destination
                        if dest_path:
                            # Get relative path from target root
                            target_root = self.path_manager.get_target_path(op.source.parent)
                            try:
                                rel_path = dest_path.relative_to(target_root)
                                print(f"  📄 Would move '{source_name}' → '{rel_path.parent}/'")
                            except ValueError:
                                print(f"  📄 Would move '{source_name}' → '{dest_path.parent}/'")
            
            print("\n💡 Run the actual organization to move the files")
        else:
            print(f"\n🎉 Organization Complete!")
            print(f"   Files processed: {result.files_processed}")
            print(f"   Files moved: {result.files_moved}")
            print(f"   Errors: {result.errors}")
            
            # Show detailed results of what was moved
            if result.operations:
                print(f"\n✅ Files moved:")
                for op in result.operations:
                    if op.operation_type.value == "move":
                        source_name = op.source.name
                        dest_path = op.destination
                        if dest_path:
                            # Get relative path from target root
                            target_root = self.path_manager.get_target_path(op.source.parent)
                            try:
                                rel_path = dest_path.relative_to(target_root)
                                print(f"  ✅ Moved '{source_name}' → '{rel_path.parent}/'")
                            except ValueError:
                                print(f"  ✅ Moved '{source_name}' → '{dest_path.parent}/'")
            
            if result.errors > 0:
                print(f"\n⚠️  Errors occurred:")
                for error in result.error_log[:5]:  # Show first 5 errors
                    print(f"   • {error}")
                if len(result.error_log) > 5:
                    print(f"   ... and {len(result.error_log) - 5} more")
        
        # Pause to let user read the results
        print("\nPress Enter to continue...")
        input()
    
    def _show_file_analysis(self, result: Any) -> None:
        """
        Show file analysis statistics.
        
        Args:
            result: Organization result containing file operations
        """
        print(f"\n📊 File Analysis")
        print("-" * 30)
        
        # Count by category
        category_counts = {}
        category_sizes = {}
        total_size = 0
        
        for op in result.operations:
            if op.operation_type.value == "move":
                # Extract category from destination path
                dest_path = op.destination
                if dest_path:
                    category = dest_path.parent.name
                    
                    # Count files
                    if category not in category_counts:
                        category_counts[category] = 0
                    category_counts[category] += 1
                    
                    # Calculate sizes
                    try:
                        size = op.source.stat().st_size
                        total_size += size
                        
                        if category not in category_sizes:
                            category_sizes[category] = 0
                        category_sizes[category] += size
                    except OSError:
                        pass  # Skip files we can't access
        
        # Display statistics
        print(f"📁 Total files: {result.files_processed}")
        print(f"💾 Total size: {self._format_size(total_size)}")
        print()
        
        print("📋 Files by category:")
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            size = category_sizes.get(category, 0)
            print(f"  {category}: {count} files ({self._format_size(size)})")
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def _view_categories(self) -> None:
        """Display current categories in a readable format."""
        print("\n📋 Current Categories:")
        print("-" * 50)
        
        config = self.config_manager.get_config()
        
        # Show configuration status
        metadata = config.get("metadata", {})
        auto_generated = metadata.get("auto_generated", False)
        version = metadata.get("version", "unknown")
        last_modified = metadata.get("last_modified", "N/A")
        
        if auto_generated:
            print(f"🔄 Auto-generated configuration (v{version})")
            print("   Use 'Manual update from defaults' to get new categories/extensions")
        else:
            print(f"✏️  User-modified configuration (v{version})")
            if last_modified != "N/A":
                print(f"   Last modified: {last_modified}")
            print("   Auto-updates disabled to preserve your customizations")
        
        print()
        
        categories = config.get("categories", {})
        for i, (name, data) in enumerate(categories.items(), 1):
            extensions = data.get("extensions", [])
            folder_name = data.get("folder_name", name)
            print(f"{i:2d}. {name}")
            print(f"    📁 Folder: {folder_name}")
            print(f"    📄 Extensions: {', '.join(extensions[:5])}{'...' if len(extensions) > 5 else ''}")
            
            # Show subcategories if they exist
            subcategories = data.get("subcategories", {})
            if subcategories:
                print(f"    📂 Subcategories: {', '.join(subcategories.keys())}")
            print()
        
        print("Press Enter to continue...")
        input()
    
    def _add_new_category(self) -> None:
        """Add a new category through interactive prompts."""
        print("\n➕ Add New Category")
        print("-" * 30)
        
        config = self.config_manager.get_config()
        categories = config.get("categories", {})
        
        # Get category name
        while True:
            name = input("Category name (e.g., 'MyFiles'): ").strip()
            if name and name not in categories:
                break
            elif name in categories:
                print("❌ Category already exists!")
            else:
                print("❌ Please enter a valid name!")
        
        # Get folder name
        folder_name = input(f"Folder name (default: {name}): ").strip()
        if not folder_name:
            folder_name = name
        
        # Get extensions
        print("Enter file extensions (including the dot, e.g., .txt, .pdf)")
        print("Press Enter twice when done:")
        extensions = []
        while True:
            ext = input(f"Extension {len(extensions)+1}: ").strip()
            if not ext:
                break
            if not ext.startswith('.'):
                ext = '.' + ext
            extensions.append(ext.lower())
        
        # Add to config
        if "categories" not in config:
            config["categories"] = {}
        
        config["categories"][name] = {
            "extensions": extensions,
            "folder_name": folder_name
        }
        
        # Set auto_generated to false since user made changes
        if "metadata" not in config:
            config["metadata"] = {}
        config["metadata"]["auto_generated"] = False
        config["metadata"]["last_modified"] = self._get_current_timestamp()
        
        if self.config_manager.set_config(config):
            print(f"✅ Added category '{name}' with {len(extensions)} extensions")
            print("📝 Configuration marked as user-modified (auto-updates disabled)")
        else:
            print("❌ Failed to save configuration!")
        print("Press Enter to continue...")
        input()
    
    def _edit_category(self) -> None:
        """Edit an existing category."""
        config = self.config_manager.get_config()
        categories = list(config.get("categories", {}).keys())
        
        if not categories:
            print("❌ No categories to edit!")
            print("Press Enter to continue...")
            input()
            return
        
        print("\n✏️  Edit Category")
        print("-" * 20)
        
        # Show categories
        for i, name in enumerate(categories, 1):
            print(f"{i}. {name}")
        
        try:
            choice = int(input(f"\nSelect category (1-{len(categories)}): ")) - 1
            if 0 <= choice < len(categories):
                category_name = categories[choice]
                self._edit_specific_category(category_name)
            else:
                print("❌ Invalid selection!")
                print("Press Enter to continue...")
                input()
        except ValueError:
            print("❌ Please enter a number!")
            print("Press Enter to continue...")
            input()
    
    def _edit_specific_category(self, category_name: str) -> None:
        """Edit a specific category's properties."""
        config = self.config_manager.get_config()
        category = config["categories"][category_name]
        
        print(f"\n✏️  Editing '{category_name}'")
        print("-" * 30)
        
        while True:
            print(f"1. Change folder name (current: {category['folder_name']})")
            print("2. Add extensions")
            print("3. Remove extensions")
            print("4. Back")
            
            choice = input("Enter choice (1-4): ").strip()
            
            if choice == "1":
                new_name = input("New folder name: ").strip()
                if new_name:
                    category["folder_name"] = new_name
                    # Set auto_generated to false since user made changes
                    if "metadata" not in config:
                        config["metadata"] = {}
                    config["metadata"]["auto_generated"] = False
                    config["metadata"]["last_modified"] = self._get_current_timestamp()
                    if self.config_manager.set_config(config):
                        print("✅ Folder name updated!")
                        print("📝 Configuration marked as user-modified (auto-updates disabled)")
                    else:
                        print("❌ Failed to save configuration!")
            
            elif choice == "2":
                ext = input("Extension to add (including dot): ").strip()
                if ext and not ext.startswith('.'):
                    ext = '.' + ext
                if ext and ext not in category["extensions"]:
                    category["extensions"].append(ext.lower())
                    # Set auto_generated to false since user made changes
                    if "metadata" not in config:
                        config["metadata"] = {}
                    config["metadata"]["auto_generated"] = False
                    config["metadata"]["last_modified"] = self._get_current_timestamp()
                    if self.config_manager.set_config(config):
                        print("✅ Extension added!")
                        print("📝 Configuration marked as user-modified (auto-updates disabled)")
                    else:
                        print("❌ Failed to save configuration!")
                else:
                    print("❌ Invalid or duplicate extension!")
            
            elif choice == "3":
                extensions = category["extensions"]
                if extensions:
                    print("Current extensions:")
                    for i, ext in enumerate(extensions, 1):
                        print(f"  {i}. {ext}")
                    try:
                        idx = int(input("Enter number to remove: ")) - 1
                        if 0 <= idx < len(extensions):
                            removed = extensions.pop(idx)
                            # Set auto_generated to false since user made changes
                            if "metadata" not in config:
                                config["metadata"] = {}
                            config["metadata"]["auto_generated"] = False
                            config["metadata"]["last_modified"] = self._get_current_timestamp()
                            if self.config_manager.set_config(config):
                                print(f"✅ Removed {removed}")
                                print("📝 Configuration marked as user-modified (auto-updates disabled)")
                            else:
                                print("❌ Failed to save configuration!")
                        else:
                            print("❌ Invalid selection!")
                    except ValueError:
                        print("❌ Please enter a number!")
                else:
                    print("❌ No extensions to remove!")
            
            elif choice == "4":
                break
    
    def _manual_update_from_defaults(self) -> None:
        """Manually update configuration from defaults with conflict resolution."""
        print("\n🔄 Manual Update from Defaults")
        print("-" * 35)
        print("This will merge new default categories and extensions with your current configuration.")
        print("Conflicts will be resolved by keeping your customizations.")
        print()
        
        config = self.config_manager.get_config()
        
        # Check if config is already auto-generated
        auto_generated = config.get("metadata", {}).get("auto_generated", False)
        if auto_generated:
            print("ℹ️  Your configuration is already auto-generated. No manual update needed.")
            print("Press Enter to continue...")
            input()
            return
        
        # Get default config
        default_config = self.config_manager.get_default_config()
        default_categories = default_config.get("categories", {})
        current_categories = config.get("categories", {})
        
        new_categories = []
        updated_categories = []
        
        for category_name, default_category in default_categories.items():
            if category_name not in current_categories:
                new_categories.append(category_name)
            else:
                # Check for new extensions
                current_extensions = set(current_categories[category_name].get("extensions", []))
                default_extensions = set(default_category.get("extensions", []))
                new_extensions = default_extensions - current_extensions
                if new_extensions:
                    updated_categories.append(f"{category_name} (+{len(new_extensions)} extensions)")
        
        if not new_categories and not updated_categories:
            print("✅ Your configuration is up to date!")
            print("Press Enter to continue...")
            input()
            return
        
        print("📋 Changes that will be applied:")
        if new_categories:
            print(f"  New categories: {', '.join(new_categories)}")
        if updated_categories:
            print(f"  Updated categories: {', '.join(updated_categories)}")
        
        print()
        confirm = input("Apply these updates? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            # Perform the update
            updated_config = self.config_manager.update_with_defaults(config)
            
            # Keep auto_generated as false since this was a manual update
            if "metadata" not in updated_config:
                updated_config["metadata"] = {}
            updated_config["metadata"]["auto_generated"] = False
            updated_config["metadata"]["last_manual_update"] = self._get_current_timestamp()
            
            if self.config_manager.set_config(updated_config):
                print("✅ Manual update completed!")
                print("📝 Configuration remains user-modified (auto-updates disabled)")
            else:
                print("❌ Failed to save configuration!")
        else:
            print("❌ Manual update cancelled.")
        
        print("Press Enter to continue...")
        input()
    
    def _reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        print("\n⚠️  Reset to Defaults")
        print("-" * 25)
        confirm = input("This will overwrite your current configuration. Continue? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            default_config = self.config_manager.get_default_config()
            if self.config_manager.set_config(default_config):
                print("✅ Configuration reset to defaults!")
                print("🔄 Auto-updates re-enabled for default configuration")
            else:
                print("❌ Failed to save configuration!")
        else:
            print("❌ Reset cancelled.")
        
        print("Press Enter to continue...")
        input()
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in the format used by the config."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _show_config_wizard(self) -> None:
        """Show configuration wizard."""
        print("\n🔧 Configuration Wizard")
        print("=" * 40)
        print("This wizard helps you customize AutoSort settings.")
        print()
        
        while True:
            print("Configuration Options:")
            print("1. View current categories")
            print("2. Add new category")
            print("3. Edit existing category")
            print("4. Manual update from defaults")
            print("5. Reset to defaults")
            print("6. Back to main menu")
            print()
            
            try:
                choice = input("Enter your choice (1-6): ").strip()
                
                if choice == "1":
                    self._view_categories()
                elif choice == "2":
                    self._add_new_category()
                elif choice == "3":
                    self._edit_category()
                elif choice == "4":
                    self._manual_update_from_defaults()
                elif choice == "5":
                    self._reset_to_defaults()
                elif choice == "6":
                    if self.config_manager.save_config():
                        print("✅ Configuration saved!")
                    else:
                        print("❌ Failed to save configuration!")
                    print("Press Enter to continue...")
                    input()
                    return
                else:
                    print("Invalid choice. Please enter 1-6.")
                    
            except KeyboardInterrupt:
                print("\nConfiguration wizard cancelled.")
                print("Press Enter to continue...")
                input()
                return
            except Exception as e:
                print(f"Error: {e}")
                print("Press Enter to continue...")
                input()
    
    def _undo_last_operation(self) -> None:
        """Undo the last operation."""
        undo_info = self.undo_manager.get_undo_info()
        
        if not undo_info['can_undo']:
            print("❌ No operations to undo")
            print("\nPress Enter to continue...")
            input()
            return
        
        print(f"↩️  Undoing: {undo_info['last_transaction']}")
        confirm = input("Continue? (y/N): ").strip().lower()
        
        if confirm in ['y', 'yes']:
            if self.undo_manager.undo_last_transaction():
                print("✅ Operation undone successfully")
            else:
                print("❌ Failed to undo operation")
        else:
            print("❌ Undo cancelled")
        
        # Pause to let user read the result
        print("\nPress Enter to continue...")
        input()
    

    
    def _go_back(self) -> None:
        """Go back to previous menu."""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
        else:
            print("Already at main menu")
    
    def _confirm_action(self) -> None:
        """Confirm current action."""
        print("✅ Action confirmed")
