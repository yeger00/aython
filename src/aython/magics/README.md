# Aython Magics - Jupyter Integration

## 🚀 Quick Start

1. **Open Jupyter Lab**: Go to `http://localhost:8888`
2. **Open the setup notebook**: Click on `aython_setup.ipynb`
3. **Run the first cell**: This loads the Aython magic commands
4. **Start using Aython**: Use the magic commands in any notebook

## 📝 Available Magic Commands

### `%init_aython <model>`
Initialize the AI agent with your preferred model.

**Examples:**
```python
%init_aython gpt-4o-mini
%init_aython gemini-1.5-flash
```

### `%code <requirements>`
Generate and execute Python code based on your requirements.

**Examples:**
```python
%code "create a function that calculates fibonacci numbers"
%code "create a data visualization with matplotlib"
%code "write a web scraper using requests and BeautifulSoup"
%code "create a machine learning model for classification"
```

### `%save_history <filename>`
Save your session history to a JSON file.

**Example:**
```python
%save_history my_session.json
```

### `%export_notebook <filename>`
Export your session as a Jupyter notebook.

**Example:**
```python
%export_notebook my_notebook.ipynb
```

## 🔧 Troubleshooting

### Magic Commands Not Working?
1. Make sure you've run the setup cell in `aython_setup.ipynb`
2. Check that the agent is running: `http://localhost:4000`
3. Verify your API keys are set in the `.env` file

### Agent Connection Issues?
1. Check agent status: `docker-compose ps`
2. View agent logs: `docker-compose logs aython-agent`
3. Restart services: `.\start-aython.ps1 -Restart`

## 📚 Example Workflow

```python
# 1. Initialize the agent
%init_aython gpt-4o-mini

# 2. Generate some code
%code "create a function that sorts a list of numbers"

# 3. Generate more complex code
%code "create a data visualization showing sales trends"

# 4. Save your work
%save_history my_work_session.json
```

## 🎯 Tips

- **Be specific**: The more detailed your requirements, the better the generated code
- **Iterate**: You can refine your requirements and generate new code
- **Save regularly**: Use `%save_history` to save your progress
- **Export notebooks**: Use `%export_notebook` to create shareable notebooks

## 🔗 Related Files

- `aython_setup.ipynb` - Setup notebook to load magics
- `aython_magics.py` - Magic commands implementation
- `start_jupyter.py` - Jupyter Lab startup script
