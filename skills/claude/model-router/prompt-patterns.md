# Model Router -- Prompt Patterns

## Pattern: Task-Appropriate Prompting

Match prompt complexity to the model tier:

### Haiku (classification)
Keep prompts short and direct. Provide clear categories.
```
Classify this text as one of: positive, negative, neutral.
Text: {text}
```

### Sonnet (reasoning)
Allow for chain-of-thought and multi-step reasoning.
```
Analyze the following data and provide:
1. Key trends
2. Anomalies
3. Recommendations

Data: {data}
```

### Opus (evaluation)
Provide rubrics and evaluation criteria.
```
Evaluate the following agent response against these criteria:
- Accuracy (1-5)
- Completeness (1-5)
- Tone (1-5)

Agent response: {response}
Expected answer: {expected}
```

## Pattern: Cascading Complexity

Start with Haiku. If confidence is below threshold, escalate to Sonnet.

```python
result = await haiku_classify(text)
if result.confidence < 0.8:
    result = await sonnet_analyze(text)
```

## Pattern: Eval-Driven Routing Updates

Use Opus evaluation results to refine routing rules. If Haiku consistently fails a task type, update routing to use Sonnet.

## Anti-Patterns

- **Never**: Use Opus for regular classification or extraction.
- **Never**: Hardcode model selection -- always go through the router.
- **Never**: Skip cost estimation before API calls.
