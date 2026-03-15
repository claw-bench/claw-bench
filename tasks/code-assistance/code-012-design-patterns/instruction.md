# Task: Implement Design Patterns

Implement the Singleton and Observer design patterns in `workspace/patterns.py`.

## Requirements

### Singleton

Implement a `Singleton` class (or metaclass/decorator) such that:

1. A class `AppConfig` uses the Singleton pattern.
2. `AppConfig()` always returns the **same instance**.
3. `AppConfig` has a `get(key)` method and a `set(key, value)` method for storing configuration.
4. The singleton should be thread-safe (use a lock).

### Observer

Implement an `EventEmitter` class:

1. `subscribe(event: str, callback: Callable)` -- Register a callback for an event.
2. `unsubscribe(event: str, callback: Callable)` -- Remove a callback for an event.
3. `emit(event: str, *args, **kwargs)` -- Call all callbacks registered for the event, passing along any args/kwargs.
4. Callbacks should be called in the order they were subscribed.

## Output

Save the file to `workspace/patterns.py`.
