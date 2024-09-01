# Igor

## 1. Introduction

### 1.1 Purpose

Igor is an event-driven multi-channel bot framework that allows users to send
and recieve messages to and from various platforms (e.g. Discord, the console,
WhatsApp, Twilio). The purpose of this document is to provide a technical
overview of Igor's architecture, components, and functionality.

### 1.2 Scope

The scope of this document covers the high-level design of Igor, including its
main components (Hub, Channels, Events, and Reactors), their responsibilities,
and interactions. It also outlines the project structure and provides guidance
on building and testing the application.

## 2. System Architecture

### 2.1 Overview

Igor consists of the the following main components:

- Hub: The central coordinator of the application, managing channels, reactors,
  and global configuration.
- Channels: Interfaces for different communication platforms (Slack, Console,
  Twilio).
- Events: A common format for communication between channels and the hub.
- Reactors: Response handlers for events, containing the logic for processing
  and replying to messages.

### 2.2 Event-Driven Architecture

Igor follows an Event-Driven Architecture pattern, which is characterized by the
following:

1. Components communicate through events: The system is composed of
   loosely coupled components (Hub, Channels, Reactors) that interact with each
   other by sending and receiving events.
2. Publish-Subscribe pattern: Channels
   publish events to the Hub, and Reactors subscribe to events they are interested
   in. This allows for a decoupled system where components don't need to know about
   each other directly.
3. Reactive system: Reactors react to incoming events and
   perform actions based on those events, processing them and determining how to
   respond.
4. Asynchronous communication: Igor uses asynchronous communication, where
   Channels don't wait for a response from Reactors after sending an event. This
   allows for a more scalable and responsive system.
5. Modularity and extensibility:
   New functionality can be added by creating new event types and corresponding
   Reactors, without modifying the existing components.

In Igor's architecture:

- The Hub acts as an "Event Bus" or "Message Broker," facilitating communication
  between components by receiving and distributing events.
- The Channels are "Adapters" that convert platform-specific interactions into a
  common event format understood by the system.
- The Reactors are "Event Handlers" that contain the business logic for
  processing specific types of events.

By using an Event-Driven Architecture, Igor is designed to be modular,
extensible, and capable of handling a variety of tasks and interactions across
multiple platforms.

### 2.3 Component Interaction

1. The Hub initializes and manages the lifecycle of Channels and Reactors.
2. Channels listen for incoming messages from their respective platforms and
   transform them into Events.
3. The Hub receives Events from Channels and queries Reactors to determine if
   they should respond.
4. Reactors evaluate the Events and execute their handling logic, which may
   involve sending a reply, performing an action, or triggering another process.
5. Channels send the Reactors' response back to the user through the appropriate
   platform.

```mermaid
graph LR
    A[Slack] --> C{Channel}
    B[Console] --> C
    D[Twilio] --> C
    C --> E[Event]
    E --> F{Hub}
    F --> G{Reactor}
    G --> H[Handler]
    H --> I[Response]
    I --> C
    F --> J[Configuration]
    F --> K[User Registry]
```

## 3. Detailed Component Design

### 3.1 Hub

The Hub is a class that holds the global config, a registry of users, and
manages the Channels and Reactors.

### 3.2 Channels

Channels are subclasses implementing a common interface for different
communication platforms. They handle the input and output of messages specific
to each platform.

They are responsible for:

- Connection management: Establish and maintain a connection with the respective
  platform.
- Message listening: Continuously listen for incoming messages from the
  platform.
- Message parsing: Convert invoming messages into a standardized format
  (Events), that the rest of the application can understand.
- Message sending: Send messages to the platform, typically as a response to an
  incoming message or a proactive message from the bot.
- Error handling; Manage any connection errors or issues with the platform's
  API.

### 3.3 Events

Events are instances of a common Event class, used by Channels to communicate
with the Hub. They encapsulate all necessary information about an event (sender,
message content, etc).

### 3.4 Reactors

Reactors are classes with predicates to determine if and how they should respond
to a given Event, and handlers to process the Event.

They are responsible for:

- Event Evaluation: Determine whether a particular event (message) should
  trigger the reactor.
- Handling Logic: Contain the logic for what to do when an event triggers the
  reactor. This could involve sending a reply, performing an action, or triggering
  another process.
- State Management: Maintain any necessary state or context needed for
  decision-making or responding to events.
- Interaction with External Services: In some cases, reactors may need to
  interact with databases, APIs, or other external services to process an event.

## 4. Functionality

Igor will support the following commands and features:

- "igor song": Retrieve and display song information
- "igor airwatch": Retrieve and display airwatch data
- "igor weather": Retrieve and display weather information
- "igor toggl start/stop": Start or stop time tracking in Toggl
- "igor fortune": Display a random fortune
- "igor remind me {in, at, on} {TIME or DURATION}: {REMINDER TEXT}": Set a reminder and send an email at the specified time
- "igor agenda": Display a list of upcoming reminders
- "igor xkcd": Daily xkcd comic strip retrieval

## 5. Project Structure

```
Igor/
│
├── main.py                  # Main application entry point
│
├── config.py                # Global configuration settings
│
├── hub.py                   # Hub class definition
│
├── events.py                # Event class and related functionalities
│
├── channels/                # Directory for channels
│   ├── __init__.py          # Makes channels a Python package
│   ├── base_channel.py      # Base class for all channels
│   ├── slack_channel.py     # Slack channel implementation
│   ├── console_channel.py   # Console channel implementation
│   └── twilio_channel.py    # Twilio channel implementation
│
├── reactors/                # Directory for reactors
│   ├── __init__.py          # Makes reactors a Python package
│   ├── base_reactor.py      # Base class for all reactors
│   └── [additional reactors]# Other specific reactors
│
├── tests/                   # Directory for tests
│   ├── __init__.py          # Makes tests a Python package
│   ├── test_hub.py          # Tests for the hub
│   ├── test_channels.py     # Tests for channel implementations
│   └── test_reactors.py     # Tests for reactor implementations
│
├── requirements.txt         # Python dependencies
│
└── README.md                # Project documentation
```

## 6. Implementation Considerations

- Use asynchronous programming (with asyncio in Python) for handling a high
  volume of messages concurrently.
- Write unit tests for each component using Python's unittest framework.
- Manage project dependencies using tools like pipenv or virtualenv.
- Store configuration and sensitive information securely, using environment
  variables or a configuration file.
