# AutoSort Troubleshooting Guide

This guide helps you resolve common issues with AutoSort.

## GUI Issues

### "tkinter is not available" Error

**Problem**: The GUI version (`autosort_gui.py`) fails to start with a tkinter import error.

**Solutions by Operating System**:

#### macOS
- **Homebrew Python**: Homebrew Python doesn't include tkinter by default
  ```bash
  brew install python-tk@3.13  # Replace 3.13 with your Python version
  ```
- **Alternative**: Install Python from [python.org](https://www.python.org/downloads/) which includes tkinter

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install python3-tk
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# For CentOS/RHEL:
sudo yum install tkinter

# For Fedora:
sudo dnf install python3-tkinter
```

#### Windows
- tkinter is usually included with Python installations
- If missing, reinstall Python from [python.org](https://www.python.org/downloads/)

**Workaround**: Use the command-line version (`autosort.py`) which doesn't require tkinter.

### GUI Window Doesn't Appear

**Problem**: The GUI script runs but no window appears.

**Solutions**:
1. Check if the window is minimized or behind other windows
2. Try running from terminal: `python3 autosort_gui.py`
3. Check terminal output for error messages
4. Ensure you have a display server running (for Linux)

## File Permission Issues

### "Permission denied" Errors

**Problem**: Cannot move files due to permission restrictions.

**Solutions**:
1. **Check file permissions**: Ensure you have read/write access to source and destination directories
2. **Run with appropriate permissions**: Don't run as root unless necessary
3. **Check file locks**: Ensure files aren't open in other applications
4. **Use .sortignore**: Add problematic files to `.sortignore` to skip them

### Cannot Create Directories

**Problem**: AutoSort cannot create the Autosort folder.

**Solutions**:
1. **Check write permissions**: Ensure you can write to the source directory
2. **Disk space**: Ensure you have sufficient disk space
3. **Path length**: Some systems have path length limitations

## Configuration Issues

### Configuration File Errors

**Problem**: JSON syntax errors in `autosort_config.json`.

**Solutions**:
1. **Validate JSON**: Use an online JSON validator
2. **Reset to defaults**: Delete `autosort_config.json` and let AutoSort recreate it
3. **Use configuration wizard**: Run AutoSort and select "Configuration wizard" to fix issues

### Categories Not Working

**Problem**: Files aren't being categorized as expected.

**Solutions**:
1. **Check extensions**: Ensure file extensions include the dot (e.g., `.txt`, not `txt`)
2. **Case sensitivity**: File extensions are case-sensitive
3. **Custom categories**: Use the configuration wizard to add custom categories
4. **Check .sortignore**: Files in `.sortignore` won't be processed

## Performance Issues

### Slow Processing

**Problem**: AutoSort is running very slowly.

**Solutions**:
1. **Large files**: Large video/image files take longer to process
2. **Many files**: Processing thousands of files will take time
3. **Use preview mode**: Use dry run mode to see what will happen first
4. **Check disk speed**: SSD vs HDD can affect performance

### Memory Issues

**Problem**: AutoSort uses too much memory.

**Solutions**:
1. **Close other applications**: Free up system memory
2. **Process in batches**: Organize smaller folders at a time
3. **Use command-line version**: GUI version uses more memory

## Installation Issues

### Python Version Problems

**Problem**: "Python 3.6+ required" error.

**Solutions**:
1. **Check Python version**: `python3 --version`
2. **Install Python 3.6+**: Download from [python.org](https://www.python.org/downloads/)
3. **Use virtual environment**: Create isolated Python environment

### Missing Dependencies

**Problem**: Import errors for required modules.

**Solutions**:
1. **Install Pillow**: `pip3 install Pillow>=10.0.0`
2. **Check Python installation**: Ensure complete Python installation
3. **Use virtual environment**: Avoid conflicts with system Python

## Common Error Messages

### "No module named '_tkinter'"
- **Cause**: tkinter not installed
- **Solution**: See "tkinter is not available" section above

### "Permission denied"
- **Cause**: Insufficient file permissions
- **Solution**: Check file/directory permissions

### "No such file or directory"
- **Cause**: Source directory doesn't exist
- **Solution**: Verify the path exists and is accessible

### "JSON decode error"
- **Cause**: Corrupted configuration file
- **Solution**: Delete `autosort_config.json` and let AutoSort recreate it

## Getting Help

If you're still experiencing issues:

1. **Check the log**: Look for detailed error messages in the output
2. **Use preview mode**: Test with dry run mode first
3. **Try command-line version**: Use `autosort.py` if GUI has issues
4. **Check file paths**: Ensure all paths are valid and accessible
5. **Review configuration**: Use the configuration wizard to check settings

## System Requirements

- **Python**: 3.6 or higher
- **Operating System**: macOS, Linux, Windows
- **Memory**: 100MB+ available RAM
- **Disk Space**: Sufficient space for file operations
- **Permissions**: Read/write access to source and destination directories

## Performance Tips

1. **Use preview mode**: Always test with dry run first
2. **Organize smaller batches**: Process folders with fewer files
3. **Close other applications**: Free up system resources
4. **Use SSD**: Faster disk access improves performance
5. **Check file sizes**: Large files take longer to process
