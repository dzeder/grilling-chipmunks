# Prompt Loader -- Prompt Patterns

## Pattern: System + User Separation

Always separate system instructions from user input. System prompts set behavior; user prompts provide the task.

```yaml
name: system-user-split
version: 1.0.0
template: |
  <system>{system_instructions}</system>
  <user>{user_input}</user>
variables:
  - system_instructions
  - user_input
```

## Pattern: Chain of Thought

Use explicit reasoning steps for complex classification or analysis tasks.

```yaml
name: chain-of-thought
version: 1.0.0
template: |
  Analyze the following input step by step:
  1. Identify the key entities.
  2. Determine the relationships.
  3. Provide your classification with confidence score.

  Input: {input_text}
variables:
  - input_text
```

## Pattern: Few-Shot Examples

Include examples in the prompt for consistent output formatting.

```yaml
name: few-shot
version: 1.0.0
template: |
  Classify the sentiment of the text.

  Example: "Great product!" -> positive
  Example: "Terrible experience." -> negative

  Text: {text}
variables:
  - text
```

## Pattern: Structured Output

Request JSON output with a defined schema.

```yaml
name: structured-output
version: 1.0.0
template: |
  Extract the following fields as JSON:
  - name (string)
  - quantity (integer)
  - priority (high|medium|low)

  Input: {input_text}
variables:
  - input_text
```

## Anti-Patterns

- **Never**: Inline prompts as raw strings in application code.
- **Never**: Use unversioned prompts in production.
- **Never**: Include secrets or PII in prompt templates.
