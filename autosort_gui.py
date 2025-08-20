#!/usr/bin/env python3
"""
AutoSort GUI - File organizer with graphical interface

A simple GUI wrapper around the AutoSort functionality.

Requirements:
- Python 3.6+
- tkinter (usually included with Python)
- macOS (for Desktop path detection and folder dialog)

Copyright (c) 2024 Gboy
Licensed under the MIT License - see LICENSE file for details.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import queue
import sys
from pathlib import Path
import os

# Import the main autosort functionality
try:
    from autosort import (
        get_desktop_path, get_downloads_path, load_config, get_extension_mapping,
        load_ignore_patterns, should_ignore, categorize_with_subfolders,
        ensure_dir, unique_path, safe_move_file, analyze_image_metadata,
        format_size
    )
except ImportError:
    messagebox.showerror("Error", "Could not import autosort.py. Please ensure it's in the same directory.")
    sys.exit(1)

class AutoSortGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoSort - File Organizer")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.source_path = tk.StringVar(value=str(get_desktop_path()))
        self.target_path = tk.StringVar()
        self.dry_run = tk.BooleanVar(value=True)
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")
        
        # Message queue for thread communication
        self.message_queue = queue.Queue()
        
        self.setup_ui()
        self.update_target_path()
        
        # Start message processing
        self.process_messages()
    
    def setup_ui(self):
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
        source_entry = ttk.Entry(main_frame, textvariable=self.source_path, width=50)
        source_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        source_entry.bind('<KeyRelease>', lambda e: self.update_target_path())
        
        # Buttons frame for source selection
        source_buttons_frame = ttk.Frame(main_frame)
        source_buttons_frame.grid(row=1, column=2, pady=5)
        
        ttk.Button(source_buttons_frame, text="Browse", command=self.browse_source).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_buttons_frame, text="Desktop", command=self.set_desktop).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_buttons_frame, text="Downloads", command=self.set_downloads).pack(side=tk.LEFT)
        
        # Target directory display
        ttk.Label(main_frame, text="Target Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        target_label = ttk.Label(main_frame, textvariable=self.target_path, foreground="darkgreen")
        target_label.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(0, weight=1)
        
        # Dry run checkbox
        dry_run_check = ttk.Checkbutton(options_frame, text="Preview mode (don't move files)", 
                                       variable=self.dry_run)
        dry_run_check.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Status label
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        # Start button
        self.start_button = ttk.Button(button_frame, text="Start Organization", 
                                      command=self.start_organization)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_button = ttk.Button(button_frame, text="Stop", 
                                     command=self.stop_organization, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT)
        
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
        self.log("AutoSort GUI started. Select a source directory and click 'Start Organization'.")
    
    def update_target_path(self):
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
    
    def browse_source(self):
        """Open folder browser for source directory."""
        directory = filedialog.askdirectory(
            title="Select Source Directory",
            initialdir=self.source_path.get()
        )
        if directory:
            self.source_path.set(directory)
            self.update_target_path()
    
    def set_desktop(self):
        """Set source directory to Desktop."""
        desktop_path = get_desktop_path()
        self.source_path.set(str(desktop_path))
        self.update_target_path()
    
    def set_downloads(self):
        """Set source directory to Downloads."""
        downloads_path = get_downloads_path()
        self.source_path.set(str(downloads_path))
        self.update_target_path()
    
    def log(self, message):
        """Add message to log."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log."""
        self.log_text.delete(1.0, tk.END)
    
    def start_organization(self):
        """Start the file organization process in a separate thread."""
        source_path = Path(self.source_path.get())
        
        if not source_path.exists():
            messagebox.showerror("Error", "Source directory does not exist!")
            return
        
        if not source_path.is_dir():
            messagebox.showerror("Error", "Source path is not a directory!")
            return
        
        # Disable start button, enable stop button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Clear log
        self.clear_log()
        
        # Start organization thread
        self.organization_thread = threading.Thread(
            target=self.run_organization,
            args=(source_path, self.dry_run.get())
        )
        self.organization_thread.daemon = True
        self.organization_thread.start()
    
    def stop_organization(self):
        """Stop the organization process."""
        self.status_var.set("Stopping...")
        # The thread will check for interruption and stop gracefully
    
    def run_organization(self, source_path, dry_run):
        """Run the organization process in a separate thread."""
        try:
            self.message_queue.put(("status", "Loading configuration..."))
            self.message_queue.put(("log", "📋 Loading configuration..."))
            
            # Load configuration
            config = load_config()
            extension_map = get_extension_mapping(config)
            
            self.message_queue.put(("log", f"✅ Loaded {len(config.get('categories', {}))} categories"))
            
            # Load ignore patterns
            patterns = load_ignore_patterns()
            if patterns:
                self.message_queue.put(("log", f"🚫 Loaded {len(patterns)} ignore patterns"))
            
            # Scan files
            self.message_queue.put(("status", "Scanning files..."))
            self.message_queue.put(("log", "🔍 Scanning files..."))
            
            files_to_process = []
            for item in source_path.iterdir():
                if (item.is_file() and 
                    not should_ignore(item.name, patterns) and
                    item.name != 'autosort.py' and 
                    item.name != 'autosort_config.json' and 
                    item.name != 'autosort_gui.py' and
                    item != source_path / 'Autosort'):
                    files_to_process.append(item)
            
            if not files_to_process:
                self.message_queue.put(("log", "✨ No files found to organize!"))
                self.message_queue.put(("complete", "No files to organize"))
                return
            
            self.message_queue.put(("log", f"📁 Found {len(files_to_process)} files to organize"))
            
            # Show file analysis
            if not dry_run:
                self.analyze_files_gui(files_to_process, extension_map, config)
            
            # Process files
            moved_count = 0
            error_count = 0
            target_root = source_path / 'Autosort'
            
            self.message_queue.put(("status", "Organizing files..."))
            self.message_queue.put(("log", "🔄 Starting organization..."))
            
            for i, item in enumerate(files_to_process, 1):
                # Check for interruption
                if hasattr(self, 'stop_requested'):
                    self.message_queue.put(("log", "⏹️ Organization stopped by user"))
                    break
                
                # Update progress
                progress = (i / len(files_to_process)) * 100
                self.message_queue.put(("progress", progress))
                self.message_queue.put(("status", f"Processing {i}/{len(files_to_process)}"))
                
                try:
                    # Categorize file
                    category, subfolder = categorize_with_subfolders(item, extension_map, config)
                    
                    # Create directory structure
                    if subfolder:
                        cat_dir = ensure_dir(target_root / category / subfolder)
                    else:
                        cat_dir = ensure_dir(target_root / category)
                    
                    dest = unique_path(cat_dir / item.name)
                    
                    if dry_run:
                        if subfolder:
                            self.message_queue.put(("log", f"  📄 Would move '{item.name}' → '{category}/{subfolder}/'"))
                        else:
                            self.message_queue.put(("log", f"  📄 Would move '{item.name}' → '{category}/'"))
                    else:
                        if safe_move_file(item, dest):
                            if subfolder:
                                self.message_queue.put(("log", f"  ✅ Moved '{item.name}' → '{category}/{subfolder}/'"))
                            else:
                                self.message_queue.put(("log", f"  ✅ Moved '{item.name}' → '{category}/'"))
                            moved_count += 1
                        else:
                            self.message_queue.put(("log", f"  ❌ Failed to move '{item.name}'"))
                            error_count += 1
                            
                except Exception as e:
                    self.message_queue.put(("log", f"  ⚠️ Error processing {item}: {e}"))
                    error_count += 1
            
            # Final status
            if dry_run:
                self.message_queue.put(("log", f"\n📋 Preview Summary: {len(files_to_process)} files would be organized"))
                self.message_queue.put(("complete", f"Preview complete: {len(files_to_process)} files"))
            else:
                self.message_queue.put(("log", f"\n🎉 Summary: {moved_count} files moved, {error_count} errors"))
                if moved_count > 0:
                    self.message_queue.put(("log", f"📁 Files organized in: {target_root}"))
                    self.message_queue.put(("log", "✨ Your files are now organized!"))
                self.message_queue.put(("complete", f"Complete: {moved_count} moved, {error_count} errors"))
                
        except Exception as e:
            self.message_queue.put(("log", f"❌ Error: {e}"))
            self.message_queue.put(("complete", f"Error: {e}"))
    
    def analyze_files_gui(self, files_to_process, extension_map, config):
        """Analyze files and show statistics in GUI."""
        self.message_queue.put(("log", "\n📊 File Analysis"))
        self.message_queue.put(("log", "-" * 30))
        
        # Count by category
        category_counts = {}
        category_sizes = {}
        total_size = 0
        
        for item in files_to_process:
            category, subfolder = categorize_with_subfolders(item, extension_map, config)
            
            # Count files
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1
            
            # Calculate sizes
            try:
                size = item.stat().st_size
                total_size += size
                
                if category not in category_sizes:
                    category_sizes[category] = 0
                category_sizes[category] += size
            except OSError:
                pass
        
        # Display statistics
        self.message_queue.put(("log", f"📁 Total files: {len(files_to_process)}"))
        self.message_queue.put(("log", f"💾 Total size: {format_size(total_size)}"))
        self.message_queue.put(("log", ""))
        
        self.message_queue.put(("log", "📋 Files by category:"))
        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            size = category_sizes.get(category, 0)
            self.message_queue.put(("log", f"  {category}: {count} files ({format_size(size)})"))
    
    def process_messages(self):
        """Process messages from the organization thread."""
        try:
            while True:
                try:
                    message_type, data = self.message_queue.get_nowait()
                    
                    if message_type == "log":
                        self.log(data)
                    elif message_type == "status":
                        self.status_var.set(data)
                    elif message_type == "progress":
                        self.progress_var.set(data)
                    elif message_type == "complete":
                        self.status_var.set(data)
                        self.start_button.config(state=tk.NORMAL)
                        self.stop_button.config(state=tk.DISABLED)
                        self.progress_var.set(0)
                        
                        # Show completion message
                        if "Error" in data:
                            messagebox.showerror("Organization Complete", data)
                        elif "No files" in data:
                            messagebox.showinfo("Organization Complete", data)
                        else:
                            messagebox.showinfo("Organization Complete", 
                                              f"Organization completed successfully!\n{data}")
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            print(f"Error processing messages: {e}")
        
        # Schedule next check
        self.root.after(100, self.process_messages)

def main():
    """Main function for the GUI application."""
    root = tk.Tk()
    app = AutoSortGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()
