import pytest
from textual.pilot import Pilot
from aython import PythonCommandPalette, CommandResult

@pytest.mark.asyncio
async def test_basic_command_execution():
    """Test that basic Python commands execute correctly"""
    async with PythonCommandPalette().run_test() as pilot:
        # Get references to widgets
        input_widget = pilot.app.query_one("#command_input")
        output_widget = pilot.app.query_one("#output")
        
        # Test simple print command
        await pilot.press("p", "r", "i", "n", "t", "(", "'", "h", "e", "l", "l", "o", "'", ")", "enter")
        await pilot.pause(0.1)  # Wait for command execution
        
        assert "hello" in output_widget.render()
        
        # Test mathematical operation
        await pilot.press("2", "+", "2", "enter")
        await pilot.pause(0.1)
        
        assert "4" in output_widget.render()

@pytest.mark.asyncio
async def test_error_handling():
    """Test that errors are properly caught and displayed"""
    async with PythonCommandPalette().run_test() as pilot:
        output_widget = pilot.app.query_one("#output")
        
        # Test syntax error
        await pilot.press("p", "r", "i", "n", "t", "(", "enter")
        await pilot.pause(0.1)
        
        assert "Error:" in output_widget.render()
        assert "error" in output_widget.classes

@pytest.mark.asyncio
async def test_clear_command():
    """Test that the clear command (Ctrl+K) works"""
    async with PythonCommandPalette().run_test() as pilot:
        output_widget = pilot.app.query_one("#output")
        
        # First add some output
        await pilot.press("p", "r", "i", "n", "t", "(", "'", "t", "e", "s", "t", "'", ")", "enter")
        await pilot.pause(0.1)
        
        assert "test" in output_widget.render()
        
        # Clear the output
        await pilot.press("ctrl+k")
        await pilot.pause(0.1)
        
        assert output_widget.render().strip() == ""

def test_command_result():
    """Test the CommandResult dataclass"""
    # Test successful command
    result = CommandResult(output="success", error=None, exit_code=0)
    assert result.output == "success"
    assert result.error is None
    assert result.exit_code == 0
    
    # Test command with error
    result = CommandResult(output="", error="error message", exit_code=1)
    assert result.error == "error message"
    assert result.exit_code == 1 