import pytest
from unittest.mock import MagicMock
from igor.reactors.base_reactor import Reactor
from igor.event import Event
from igor.response import Response
from igor.hub import Hub


class DummyReactor(Reactor):
    def can_handle(self, event: Event) -> bool:
        return event.event_type == "test"

    def handle(self, event: Event) -> Response:
        return Response(content=f"Handled: {event.content}", channel=event.channel)


@pytest.fixture
def hub():
    return MagicMock(spec=Hub)


@pytest.fixture
def reactor(hub):
    return DummyReactor(hub)


def test_reactor_initialization(reactor, hub):
    assert isinstance(reactor, Reactor)
    assert reactor.hub == hub


def test_reactor_can_handle(reactor):
    can_handle_event = Event(
        event_type="test", content="can handle", channel="test_channel"
    )
    cannot_handle_event = Event(
        event_type="other", content="cannot handle", channel="test_channel"
    )

    assert reactor.can_handle(can_handle_event)
    assert not reactor.can_handle(cannot_handle_event)


def test_reactor_handle(reactor):
    event = Event(event_type="test", content="test content", channel="test_channel")
    response = reactor.handle(event)

    assert isinstance(response, Response)
    assert response.content == "Handled: test content"
    assert response.channel == "test_channel"


@pytest.mark.asyncio
async def test_reactor_in_hub(hub, reactor):
    event = Event(event_type="test", content="test content", channel="test_channel")

    # Simulate Hub's process_event method
    if reactor.can_handle(event):
        response = reactor.handle(event)
        await hub.send_channel_response(event, response)

    # Use assert_awaited_once() and then check the call arguments
    hub.send_channel_response.assert_awaited_once()
    call_args = hub.send_channel_response.await_args
    assert call_args is not None, "send_channel_response was not called"

    called_event, called_response = call_args[0]
    assert called_event == event
    assert isinstance(called_response, Response)
    assert called_response.content == "Handled: test content"
    assert called_response.channel == "test_channel"
