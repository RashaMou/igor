import pytest
from igor.reactors.echoreactor import EchoReactor
from igor.response import Response
from igor.event import Event


@pytest.fixture
def echoreactor(hub):
    # return EchoReactor(hub)
    reactor = next((r for r in hub.reactors if isinstance(r, EchoReactor)), None)
    if not reactor:
        reactor = EchoReactor(hub)
        hub.reactors.append(reactor)
    return reactor


def test_can_handle(echoreactor):
    # Test cases that should return True
    assert echoreactor.can_handle(
        Event(type="message", content="igor echo hello", channel="console")
    )
    assert echoreactor.can_handle(
        Event(type="message", content="IGOR ECHO test", channel="console")
    )

    # Test cases that should return False
    assert not echoreactor.can_handle(
        Event(type="message", content="hello igor", channel="console")
    )
    assert not echoreactor.can_handle(
        Event(type="not_message", content="igor echo test", channel="console")
    )


@pytest.mark.asyncio
def test_handle(echoreactor):
    # test with a message
    event = Event(type="message", content="Igor echo yo hey", channel="console")

    response = echoreactor.handle(event)
    assert isinstance(response, Response)
    assert response.content == "yo hey"

    # test with an empty message
    event = Event(type="message", content="Igor echo", channel="console")

    response = echoreactor.handle(event)
    assert response.content == "You didn't say anything"

    # test with trailing whitespace
    event = Event(type="message", content="Igor echo heyo ", channel="console")

    response = echoreactor.handle(event)
    assert response.content == "heyo"

    # test with leading whitespace
    event = Event(type="message", content=" Igor echo heyo", channel="console")

    response = echoreactor.handle(event)
    assert response.content == "heyo"
