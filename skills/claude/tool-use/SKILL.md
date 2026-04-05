# Tool Use Skill

## Purpose

Define and validate tool schemas for Claude's tool use capability. Tool use is preferred over freeform JSON for all structured interactions. Every tool must have a validated schema before it can be called by an agent.

## Constraints

- **Tool use over freeform JSON** -- always use Claude's native tool_use feature instead of asking for JSON in the prompt.
- **Schema required** -- every tool must have a Pydantic model defining its input and output.
- **Validation before call** -- inputs are validated against the schema before the tool is invoked.
- **Result validation** -- tool results are validated against the output schema before returning to the model.
- **Error wrapping** -- tool errors are wrapped in a standard error format, never raw exceptions.
- **Idempotency** -- tools should be idempotent where possible. Document side effects explicitly.

## Supported Operations

- `register_tool` -- Register a new tool with its schema.
- `validate_input` -- Validate tool input against its schema.
- `validate_output` -- Validate tool output against its schema.
- `list_tools` -- List all registered tools.
- `get_tool_schema` -- Get the schema for a specific tool in Claude API format.

## Inputs

- `tool_name`: Name of the tool.
- `operation`: The operation to perform.
- `input_data`: Tool input to validate (for validate_input).
- `output_data`: Tool output to validate (for validate_output).
- `schema_definition`: Pydantic model class path (for register_tool).

## Outputs

- `valid`: Boolean indicating validation result.
- `errors`: List of validation errors.
- `tool_schema`: Tool schema in Claude API format.
- `registered_tools`: List of registered tool names.

## Dependencies

- `context-manager` skill for tracking tool result token usage.
