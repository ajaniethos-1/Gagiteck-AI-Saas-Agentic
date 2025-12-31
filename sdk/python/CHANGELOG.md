# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-01

### Added
- Initial release of Gagiteck Python SDK
- `Client` class for API interactions
  - Agents API: list, create, get, update, delete, run
  - Workflows API: list, create, get, update, delete, trigger
  - Executions API: list, get
- `Agent` class for local agent creation
  - Support for custom system prompts
  - Conversation memory (optional)
  - Tool integration
- `Tool` class and `@tool` decorator
  - Automatic parameter schema generation from type hints
  - Support for sync and async functions
- Exception classes
  - `GagiteckError` - Base exception
  - `APIError` - API errors with status codes
  - `AuthenticationError` - Auth failures
  - `RateLimitError` - Rate limit exceeded
  - `ValidationError` - Invalid input
  - `ToolError` - Tool execution failures
- Full type annotations for IDE support
- Comprehensive test suite

### Notes
- Async client support coming in v0.2.0
- Streaming responses coming in v0.2.0
