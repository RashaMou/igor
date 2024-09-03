import pytest
import asyncio
from igor.channels.console import Console
from igor.event import Event


def test_console_creation(hub_with_mocked_process):
    console = Console(hub_with_mocked_process)
    assert isinstance(console, Console)
    assert console.hub == hub_with_mocked_process


@pytest.mark.asyncio
async def test_start_listening(hub_with_mocked_process):
    console = Console(hub_with_mocked_process)

    # Create a queue for input simulation
    input_queue = asyncio.Queue()
    await input_queue.put("igor hello")
    await input_queue.put("q")

    # Mock async_input to get values from the queue
    async def mock_async_input(prompt):
        return await input_queue.get()

    console.async_input = mock_async_input

    # Run start_listening in a separate task
    listen_task = asyncio.create_task(console.start_listening())

    # Wait for the task to complete or timeout
    try:
        await asyncio.wait_for(listen_task, timeout=2.0)
    except asyncio.TimeoutError:
        listen_task.cancel()
        await asyncio.gather(listen_task, return_exceptions=True)

    # Verify that process_event was called with the correct event
    hub = hub_with_mocked_process
    hub.process_event.assert_called_once()
    hub.signal_shutdown.assert_called_once()

    called_event = hub.process_event.call_args[0][0]
    assert isinstance(called_event, Event)
    assert called_event.content == "igor hello"
    assert called_event.channel == "console"
