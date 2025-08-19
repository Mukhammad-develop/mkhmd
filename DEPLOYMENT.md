# PythonAnywhere Deployment Guide

## Prerequisites for Turnitin Automation

The Turnitin automation feature requires Chrome browser and ChromeDriver to work on the server. Here's how to set it up on PythonAnywhere:

### 1. Install Dependencies

```bash
# In PythonAnywhere console
pip3.10 install --user -r requirements.txt
```

### 2. Chrome Setup on PythonAnywhere

**Note**: PythonAnywhere free accounts don't support browser automation due to security restrictions. You'll need a **Hacker plan** or higher.

For paid accounts:
```bash
# Install Chrome (if not already installed)
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install google-chrome-stable
```

### 3. Environment Configuration

The code automatically detects PythonAnywhere environment and configures Chrome options accordingly:

- Headless mode enabled
- Optimized memory usage
- Server-friendly Chrome arguments
- Automatic ChromeDriver management via webdriver-manager

### 4. File Upload Limits

- Maximum file size: 10MB
- Supported formats: .docx, .pdf, .pptx
- Temporary files are automatically cleaned up

### 5. Troubleshooting

If automation fails:

1. **Check Chrome Installation**:
   ```bash
   google-chrome --version
   ```

2. **Check ChromeDriver**:
   ```bash
   python3 -c "from webdriver_manager.chrome import ChromeDriverManager; print(ChromeDriverManager().install())"
   ```

3. **Memory Issues**: 
   - The code includes memory optimization for server environments
   - Screenshots are saved to `/tmp` on servers

4. **Network Issues**:
   - Ensure external HTTP requests are allowed
   - Check if Turnitin website is accessible

### 6. Alternative for Free Accounts

If browser automation isn't available, consider:
- Using a headless browser service
- Implementing file processing without browser automation
- Using API-based solutions if available

## Local Development vs Production

The code automatically detects the environment:
- **Local Mac**: Uses Homebrew ChromeDriver
- **PythonAnywhere/Linux**: Uses webdriver-manager
- **Screenshots**: Saved to project directory locally, `/tmp` on servers

## Security Notes

- Files are processed in temporary directories
- Temporary files are automatically cleaned up
- No sensitive data is stored permanently
- All automation happens in headless mode 