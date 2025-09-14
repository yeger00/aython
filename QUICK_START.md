# Aython Quick Start Guide

## 🚀 **Ready to Use!**

Your Aython system is now fully integrated and ready to run. Here's everything you need to know:

## 📁 **What You Have**

### **Core System**
- ✅ **Integrated Agent**: Code generation + execution in one service
- ✅ **Jupyter Magics**: Easy-to-use magic commands
- ✅ **Docker Setup**: Everything containerized
- ✅ **Management Scripts**: Easy start/stop/control

### **Files Created**
- `start-aython.ps1` - Main management script
- `stop-aython.ps1` - Quick shutdown script  
- `start-aython.bat` - Windows batch wrapper
- `stop-aython.bat` - Windows batch wrapper
- `DOCKER_SETUP.md` - Detailed setup guide
- `SCRIPTS_README.md` - Script documentation
- `ARCHITECTURE.md` - System architecture

## 🎯 **Quick Start (3 Steps)**

### **Step 1: Navigate to Directory**
```powershell
cd src/aython
```

### **Step 2: Start Services**
```powershell
# PowerShell (Recommended)
.\start-aython.ps1

# OR Windows Batch
start-aython.bat
```

### **Step 3: Use Aython**
1. Open browser: `http://localhost:8888`
2. In Jupyter notebook:
   ```python
   %init_aython gpt-4o-mini
   %code "create a function that calculates fibonacci numbers"
   ```

## 🛠️ **Management Commands**

| Action | Command |
|--------|---------|
| **Start** | `.\start-aython.ps1` |
| **Stop** | `.\start-aython.ps1 -Stop` |
| **Status** | `.\start-aython.ps1 -Status` |
| **Logs** | `.\start-aython.ps1 -Logs` |
| **Restart** | `.\start-aython.ps1 -Restart` |
| **Help** | `.\start-aython.ps1 -Help` |

## 🔧 **First Time Setup**

1. **Create .env file** (script will help you):
   ```bash
   MODEL=gpt-4o-mini
   OPENAI_API_KEY=your_api_key_here
   AGENT_PORT=4000
   ```

2. **Start services**:
   ```powershell
   .\start-aython.ps1
   ```

3. **Access Jupyter Lab**: `http://localhost:8888`

## 📊 **What's Running**

When started, you'll have:
- **Agent Service**: `http://localhost:4000` (JSON-RPC API)
- **Jupyter Lab**: `http://localhost:8888` (Web interface)

## 🎮 **Using Aython**

### **Magic Commands**
```python
# Initialize agent
%init_aython gpt-4o-mini

# Generate and execute code
%code "create a data visualization with matplotlib"

# Save session
%save_history my_session.json

# Export notebook
%export_notebook my_notebook.ipynb
```

### **Example Workflows**
```python
# Data Analysis
%code "load a CSV file and show basic statistics"

# Machine Learning
%code "create a simple linear regression model"

# Web Scraping
%code "scrape data from a website using requests and BeautifulSoup"

# API Integration
%code "create a function to call a REST API"
```

## 🚨 **Troubleshooting**

### **Services Won't Start**
```powershell
# Check status
.\start-aython.ps1 -Status

# View logs
.\start-aython.ps1 -Logs

# Restart
.\start-aython.ps1 -Restart
```

### **Common Issues**
1. **Docker not running**: Start Docker Desktop
2. **API key missing**: Edit `.env` file
3. **Port conflicts**: Check if ports 4000/8888 are free
4. **Permission issues**: Run PowerShell as Administrator

## 🎉 **You're All Set!**

Your Aython system is now:
- ✅ **Fully Integrated**: No separate executor needed
- ✅ **Docker Ready**: Everything containerized
- ✅ **Easy to Use**: Simple management scripts
- ✅ **Production Ready**: Built for scaling

**Next Steps:**
1. Run `.\start-aython.ps1`
2. Open `http://localhost:8888`
3. Start coding with AI!

---

**Need Help?** Check `SCRIPTS_README.md` for detailed documentation.
