# Reactors are response handlers for events. Each reactor can be a class with
# predicates to determine if it should respond to a given event, and handlers to
# process the event. Use Python functions or callable objects as handlers.
# Handlers should be able to access the event's data and use event.Reply() to
# send responses back through the appropriate channel.
