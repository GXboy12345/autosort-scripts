"""
Graphical User Interface for AutoSort

A modern GUI implementation with enhanced features, real-time progress,
and better user experience.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import logging
from pathlib import Path
from typing import Optional

from core.config_manager import ConfigManager
from core.file_organizer import FileOrganizer
from core.path_manager import PathManager
from utils.undo_manager import UndoManager

from utils.logger import setup_logging

logger = logging.getLogger(__name__)


class AutoSortGUI:
    """
    Enhanced GUI interface for AutoSort.
    
    Provides a modern, user-friendly interface with real-time progress,
    detailed logging, and enhanced features.
    """
    
    def __init__(self, config_manager: ConfigManager, file_organizer: FileOrganizer,
                 undo_manager: UndoManager):
        """
        Initialize the GUI interface.
        
        Args:
            config_manager: Configuration manager instance
            file_organizer: File organizer instance
            undo_manager: Undo manager instance
        """
        self.config_manager = config_manager
        self.file_organizer = file_organizer
        self.undo_manager = undo_manager
        self.path_manager = PathManager()
        
        # GUI state
        self.root = None
        self.source_path = None
        self.target_path = None
        self.dry_run = None
        self.progress_var = None
        self.status_var = None
        self.log_text = None
        self.start_button = None
        self.stop_button = None
        self.undo_button = None
        self.organization_thread = None
        self.message_queue = queue.Queue()
        self.stop_requested = False
        
        logger.info("GUI interface initialized")
    
    def run(self) -> int:
        """
        Run the GUI interface.
        
        Returns:
            Exit code
        """
        try:
            self._create_window()
            self._setup_ui()
            self._process_messages()
            self.root.mainloop()
            return 0
            
        except Exception as e:
            logger.error(f"GUI error: {e}")
            return 1
    
    def _create_window(self):
        """Create the main window."""
        self.root = tk.Tk()
        self.root.title("AutoSort - File Organizer")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Set window icon if available
        try:
            # You can add an icon file here
            pass
        except:
            pass
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="AutoSort - File Organizer", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Source directory selection
        ttk.Label(main_frame, text="Source Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.source_path = tk.StringVar(value=str(self.path_manager.get_desktop_path()))
        source_entry = ttk.Entry(main_frame, textvariable=self.source_path, width=50)
        source_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        source_entry.bind('<KeyRelease>', lambda e: self._update_target_path())
        
        # Buttons frame for source selection
        source_buttons_frame = ttk.Frame(main_frame)
        source_buttons_frame.grid(row=1, column=2, pady=5)
        
        ttk.Button(source_buttons_frame, text="Browse", command=self._browse_source).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_buttons_frame, text="Desktop", command=self._set_desktop).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_buttons_frame, text="Downloads", command=self._set_downloads).pack(side=tk.LEFT)
        
        # Target directory display
        ttk.Label(main_frame, text="Target Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.target_path = tk.StringVar()
        target_label = ttk.Label(main_frame, textvariable=self.target_path, foreground="darkgreen")
        target_label.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(0, weight=1)
        
        # Dry run checkbox
        self.dry_run = tk.BooleanVar(value=True)
        dry_run_check = ttk.Checkbutton(options_frame, text="Preview mode (don't move files)", 
                                       variable=self.dry_run)
        dry_run_check.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Undo info
        undo_info = self.undo_manager.get_undo_info()
        if undo_info['can_undo']:
            undo_text = f"Can undo: {undo_info['last_transaction']}"
            undo_label = ttk.Label(options_frame, text=undo_text, foreground="blue")
            undo_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Start button
        self.start_button = ttk.Button(button_frame, text="Start Organization", 
                                      command=self._start_organization)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self._stop_organization, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Undo button
        self.undo_button = ttk.Button(button_frame, text="Undo Last", 
                                     command=self._undo_last_operation)
        self.undo_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        ttk.Button(button_frame, text="Clear Log", command=self._clear_log).pack(side=tk.LEFT)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initial log message
        self._log("AutoSort GUI started. Select a source directory and click 'Start Organization'.")
        self._update_target_path()
    
    def _update_target_path(self):
        """Update the target path based on source path."""
        try:
            source = Path(self.source_path.get())
            if source.exists() and source.is_dir():
                target = source / 'Autosort'
                self.target_path.set(str(target))
            else:
                self.target_path.set("Invalid source directory")
        except Exception:
            self.target_path.set("Error")
    
    def _browse_source(self):
        """Open folder browser for source directory."""
        directory = filedialog.askdirectory(
            title="Select Source Directory",
            initialdir=self.source_path.get()
        )
        if directory:
            self.source_path.set(directory)
            self._update_target_path()
    
    def _set_desktop(self):
        """Set source directory to Desktop."""
        desktop_path = self.path_manager.get_desktop_path()
        self.source_path.set(str(desktop_path))
        self._update_target_path()
    
    def _set_downloads(self):
        """Set source directory to Downloads."""
        downloads_path = self.path_manager.get_downloads_path()
        self.source_path.set(str(downloads_path))
        self._update_target_path()
    
    def _log(self, message):
        """Add message to log."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def _clear_log(self):
        """Clear the log."""
        self.log_text.delete(1.0, tk.END)
    
    def _start_organization(self):
        """Start the file organization process in a separate thread."""
        source_path = Path(self.source_path.get())
        
        # Validate path (same as CLI)
        path_info = self.path_manager.validate_path(source_path)
        if not path_info.exists or not path_info.is_directory:
            messagebox.showerror("Error", f"Invalid directory: {source_path}")
            return
        
        # Disable start button, enable stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Clear log
        self._clear_log()
        
        # Start organization thread
        self.organization_thread = threading.Thread(
            target=self._run_organization,
            args=(source_path, self.dry_run.get())
        )
        self.organization_thread.daemon = True
        self.organization_thread.start()
    
    def _stop_organization(self):
        """Stop the organization process."""
        self.stop_requested = True
        self.status_var.set("Stopping...")
        self._log("⏹️ Organization stopped by user")
    
    def _undo_last_operation(self):
        """Undo the last operation."""
        undo_info = self.undo_manager.get_undo_info()
        
        if not undo_info['can_undo']:
            messagebox.showinfo("Info", "No operations to undo")
            return
        
        result = messagebox.askyesno("Confirm Undo", 
                                   f"Undo: {undo_info['last_transaction']}\n\nContinue?")
        
        if result:
            if self.undo_manager.undo_last_transaction():
                self._log("✅ Operation undone successfully")
                messagebox.showinfo("Success", "Operation undone successfully")
            else:
                self._log("❌ Failed to undo operation")
                messagebox.showerror("Error", "Failed to undo operation")
    
    def _run_organization(self, source_path, dry_run):
        """Run the organization process in a separate thread."""
        try:
            self.message_queue.put(("status", "Loading configuration..."))
            self.message_queue.put(("log", "📋 Loading configuration..."))
            
            # Load configuration
            if not self.config_manager.load_config():
                self.message_queue.put(("log", "❌ Failed to load configuration"))
                self.message_queue.put(("complete", "Configuration error"))
                return
            
            config = self.config_manager.get_categories()
            self.message_queue.put(("log", f"✅ Loaded {len(config)} categories"))
            
            # Load ignore patterns
            ignore_file = Path(".sortignore")
            self.file_organizer.load_ignore_patterns(ignore_file)
            
            # Analyze files
            self.message_queue.put(("status", "Analyzing files..."))
            self.message_queue.put(("log", "🔍 Analyzing files..."))
            
            analysis = self.file_organizer.analyze_files(source_path)
            
            if not analysis['total_files']:
                self.message_queue.put(("log", "✨ No files found to organize!"))
                self.message_queue.put(("complete", "No files to organize"))
                return
            
            self.message_queue.put(("log", f"📁 Found {analysis['total_files']} files to organize"))
            
            # Show file analysis
            self.message_queue.put(("log", f"📊 Total size: {self._format_size_gui(analysis['total_size'])}"))
            for category, stats in analysis['categories'].items():
                self.message_queue.put(("log", f"  {category}: {stats['count']} files"))
            
            # Set up progress callback
            def progress_callback(current, total, filename):
                progress = (current / total) * 100 if total > 0 else 0
                self.message_queue.put(("progress", progress))
                self.message_queue.put(("status", f"Processing {current}/{total} - {filename}"))
            
            self.file_organizer.set_progress_callback(progress_callback)
            
            # Start undo transaction if not dry run
            transaction_id = None
            if not dry_run:
                description = f"Organize {source_path.name}"
                transaction_id = self.undo_manager.start_transaction(description)
                # Set current transaction in file organizer
                self.file_organizer.set_current_transaction(transaction_id)
            
            # Organize files
            self.message_queue.put(("status", "Organizing files..."))
            self.message_queue.put(("log", "🔄 Starting organization..."))
            
            result = self.file_organizer.organize_directory(source_path, dry_run=dry_run)
            
            # Show results
            if dry_run:
                self.message_queue.put(("log", f"\n📋 Preview Summary:"))
                self.message_queue.put(("log", f"   Files that would be organized: {result.files_processed}"))
                self.message_queue.put(("log", f"   Categories: {len(result.operations)}"))
                
                # Show file analysis
                if result.files_processed > 0:
                    self._show_file_analysis_gui(result)
                
                # Show detailed preview of what would happen
                if result.operations:
                    self.message_queue.put(("log", f"\n📄 Files that would be moved:"))
                    for op in result.operations:
                        if op.operation_type.value == "move":
                            source_name = op.source.name
                            dest_path = op.destination
                            if dest_path:
                                # Get relative path from target root
                                target_root = self.path_manager.get_target_path(op.source.parent)
                                try:
                                    rel_path = dest_path.relative_to(target_root)
                                    self.message_queue.put(("log", f"  📄 Would move '{source_name}' → '{rel_path.parent}/'"))
                                except ValueError:
                                    self.message_queue.put(("log", f"  📄 Would move '{source_name}' → '{dest_path.parent}/'"))
                
                self.message_queue.put(("log", "\n💡 Uncheck 'Preview mode' to actually move the files"))
            else:
                self.message_queue.put(("log", f"\n🎉 Organization Complete!"))
                self.message_queue.put(("log", f"   Files processed: {result.files_processed}"))
                self.message_queue.put(("log", f"   Files moved: {result.files_moved}"))
                self.message_queue.put(("log", f"   Errors: {result.errors}"))
                
                # Show detailed results of what was moved
                if result.operations:
                    self.message_queue.put(("log", f"\n✅ Files moved:"))
                    for op in result.operations:
                        if op.operation_type.value == "move":
                            source_name = op.source.name
                            dest_path = op.destination
                            if dest_path:
                                # Get relative path from target root
                                target_root = self.path_manager.get_target_path(op.source.parent)
                                try:
                                    rel_path = dest_path.relative_to(target_root)
                                    self.message_queue.put(("log", f"  ✅ Moved '{source_name}' → '{rel_path.parent}/'"))
                                except ValueError:
                                    self.message_queue.put(("log", f"  ✅ Moved '{source_name}' → '{dest_path.parent}/'"))
                
                if result.errors > 0:
                    self.message_queue.put(("log", f"\n⚠️  Errors occurred:"))
                    for error in result.error_log[:5]:  # Show first 5 errors
                        self.message_queue.put(("log", f"   • {error}"))
                    if len(result.error_log) > 5:
                        self.message_queue.put(("log", f"   ... and {len(result.error_log) - 5} more"))
                
                # Commit transaction if successful
                if transaction_id and result.success:
                    self.undo_manager.commit_transaction(transaction_id)
                    self.message_queue.put(("log", "✅ Transaction saved for undo"))
            
            self.message_queue.put(("complete", "Organization complete"))
            
        except Exception as e:
            logger.error(f"Organization error: {e}")
            self.message_queue.put(("log", f"❌ Error: {e}"))
            self.message_queue.put(("complete", "Error occurred"))
    
    def _process_messages(self):
        """Process messages from the organization thread."""
        try:
            while True:
                try:
                    message_type, data = self.message_queue.get_nowait()
                    
                    if message_type == "log":
                        self._log(data)
                    elif message_type == "status":
                        self.status_var.set(data)
                    elif message_type == "progress":
                        self.progress_var.set(data)
                    elif message_type == "complete":
                        self._organization_complete()
                        break
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            logger.error(f"Message processing error: {e}")
        
        # Schedule next check
        self.root.after(100, self._process_messages)
    
    def _organization_complete(self):
        """Handle organization completion."""
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.stop_requested = False
        self.status_var.set("Ready")
        
        # Update undo button state
        undo_info = self.undo_manager.get_undo_info()
        if undo_info['can_undo']:
            self.undo_button.config(state=tk.NORMAL)
        else:
            self.undo_button.config(state=tk.DISABLED)
    
    def _show_file_analysis_gui(self, result):
        """
        Show file analysis statistics in GUI.
        
        Args:
            result: Organization result containing file operations
        """
        self.message_queue.put(("log", f"\n📊 File Analysis"))
        self.message_queue.put(("log", "-" * 30))
        
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
        self.message_queue.put(("log", f"📁 Total files: {result.files_processed}"))
        self.message_queue.put(("log", f"💾 Total size: {self._format_size_gui(total_size)}"))
        self.message_queue.put(("log", ""))
        
        self.message_queue.put(("log", "📋 Files by category:"))
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            size = category_sizes.get(category, 0)
            self.message_queue.put(("log", f"  {category}: {count} files ({self._format_size_gui(size)})"))
    
    def _format_size_gui(self, size_bytes):
        """
        Format file size in human-readable format for GUI.
        
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


class GUIInterface:
    """
    GUI interface wrapper for AutoSort.
    
    This class provides the interface between the main application
    and the GUI implementation.
    """
    
    def __init__(self, config_manager: ConfigManager, file_organizer: FileOrganizer,
                 undo_manager: UndoManager):
        """
        Initialize the GUI interface.
        
        Args:
            config_manager: Configuration manager instance
            file_organizer: File organizer instance
            undo_manager: Undo manager instance
        """
        self.config_manager = config_manager
        self.file_organizer = file_organizer
        self.undo_manager = undo_manager
        
        # Connect file organizer to undo manager
        if hasattr(self.file_organizer, 'undo_manager'):
            self.file_organizer.undo_manager = self.undo_manager
        
        logger.info("GUI interface initialized")
    
    def run(self) -> int:
        """
        Run the GUI interface.
        
        Returns:
            Exit code
        """
        try:
            gui = AutoSortGUI(
                self.config_manager,
                self.file_organizer,
                self.undo_manager
            )
            return gui.run()
            
        except Exception as e:
            logger.error(f"GUI error: {e}")
            return 1