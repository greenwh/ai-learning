# Multi-Model AI Provider Compatibility Guide

**A comprehensive guide to handling compatibility issues across OpenAI, Google Gemini, Anthropic Claude, and xAI models**

Last Updated: 2025-11-08

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Common Compatibility Issues](#common-compatibility-issues)
3. [Model-Specific Quirks](#model-specific-quirks)
4. [Implementation Patterns](#implementation-patterns)
5. [Testing Strategies](#testing-strategies)
6. [Code Examples](#code-examples)

---

## Executive Summary

When building applications that support multiple AI providers, you'll encounter three major categories of compatibility issues:

1. **Parameter Restrictions** - Models that reject certain parameter values
2. **API Structure Variations** - Different response formats and access patterns
3. **Library Version Mismatches** - SDK versions that don't match API capabilities

This guide documents real-world solutions for these issues based on production experience.

---

## Common Compatibility Issues

### 1. Temperature Parameter Restrictions

**Problem**: Some models only support default temperature values.

**Affected Models**:
- OpenAI `gpt-5-nano` - Only supports temperature=1.0 (default)
- OpenAI `o1` series - Fixed temperature, parameter not accepted at all
- OpenAI `o3` series - Fixed temperature, parameter not accepted at all

**Solution Pattern**:
```python
try:
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature
    )
except Exception as e:
    if "temperature" in str(e) and "not support" in str(e).lower():
        # Retry without temperature parameter
        response = client.chat.completions.create(
            model=model_name,
            messages=messages
            # temperature omitted = uses model default
        )
```

**Key Insight**: Don't set temperature to 1.0 - completely omit the parameter to use defaults.

---

### 2. Token Limit Parameter Naming

**Problem**: Different models use different parameter names for token limits.

**Parameter Variations**:
- `max_tokens` - Standard parameter (GPT-3.5, GPT-4, most models)
- `max_completion_tokens` - Newer parameter (O1, O3, some GPT-5 models)
- `max_output_tokens` - Google Gemini parameter

**Affected Models**:
| Model Family | Parameter Name | Notes |
|--------------|----------------|-------|
| gpt-3.5-* | `max_tokens` | Standard |
| gpt-4-* | `max_tokens` | Standard |
| gpt-5-* | Varies | Some use `max_completion_tokens` |
| o1-* | `max_completion_tokens` | Only this parameter |
| o3-* | `max_completion_tokens` | Only this parameter |
| gemini-* | `max_output_tokens` | In generation_config |

**Solution Pattern**:
```python
# Try primary parameter first
try:
    if model.startswith('o1') or model.startswith('o3'):
        # These definitely need max_completion_tokens
        kwargs['max_completion_tokens'] = max_tokens
    else:
        # Try max_tokens first for others
        kwargs['max_tokens'] = max_tokens

    response = client.create(**kwargs)
except Exception as e:
    # Check error message for what's actually needed
    if 'max_completion_tokens' in str(e):
        del kwargs['max_tokens']
        kwargs['max_completion_tokens'] = max_tokens
        response = client.create(**kwargs)
```

---

### 3. Library Version vs API Capability Mismatch

**Problem**: Python library doesn't support parameters that the API accepts (or vice versa).

**Symptoms**:
- `TypeError: unexpected keyword argument 'max_completion_tokens'`
- API returns: "Use max_completion_tokens not max_tokens"
- Both of the above for the same model!

**Solution Pattern**:
```python
try:
    # Try what the API wants
    response = client.create(max_completion_tokens=tokens)
except TypeError:
    # Library doesn't support it, try alternative
    response = client.create(max_tokens=tokens)
except APIError as e:
    if 'max_completion_tokens' in str(e):
        # API wants different param, try that
        response = client.create(max_completion_tokens=tokens)
```

---

### 4. Google Gemini Response Extraction

**Problem**: Gemini's response structure varies across library versions and can be complex to extract text from.

**Library Versions**:
- `google-generativeai==0.3.2` (older) - Different response structure
- `google-generativeai>=0.4.0` (newer) - Improved but still complex

**Response Structure Variations**:
```python
# Method 1: Parts-based extraction (most reliable)
response.candidates[0].content.parts[0].text

# Method 2: Direct text accessor (simple responses only)
response.text

# Method 3: Candidate text (some versions)
response.candidates[0].text

# Method 4: Alternative parts access
response.parts[0].text
```

**Common Errors**:
1. **"response.text only works for simple text responses"** - Multi-part response detected
2. **"Gemini returned no candidates"** - Safety filters blocked the response
3. **Empty parts list** - Response structure exists but no actual text

**Comprehensive Solution**:
```python
def extract_gemini_text(response):
    # Check for candidates
    if not response.candidates:
        raise Exception("No candidates - likely blocked by safety filters")

    candidate = response.candidates[0]

    # Check for safety blocks
    if hasattr(candidate, 'finish_reason'):
        if 'SAFETY' in str(candidate.finish_reason):
            raise Exception(f"Blocked: {candidate.finish_reason}")

    # Try Method 1: Extract from parts (most reliable)
    if candidate.content and candidate.content.parts:
        text_parts = []
        for part in candidate.content.parts:
            # Try multiple access patterns
            if hasattr(part, 'text') and part.text:
                text_parts.append(part.text)
            elif isinstance(part, dict) and 'text' in part:
                text_parts.append(part['text'])

        if text_parts:
            return ''.join(text_parts)

    # Try Method 2: Direct text accessor
    try:
        if response.text:
            return response.text
    except:
        pass

    # Try Method 3: Candidate text
    try:
        if hasattr(candidate, 'text') and candidate.text:
            return candidate.text
    except:
        pass

    # Try Method 4: Response parts
    if hasattr(response, 'parts') and response.parts:
        text_parts = [p.text for p in response.parts if hasattr(p, 'text')]
        if text_parts:
            return ''.join(text_parts)

    raise Exception("Could not extract text from response")
```

---

## Model-Specific Quirks

### OpenAI Models

#### GPT-3.5 and GPT-4 Series
- ✅ Standard parameters work
- ✅ Temperature: 0.0 - 2.0
- ✅ Parameter: `max_tokens`
- ⚠️ Some newer GPT-4 variants may have restrictions

#### GPT-5 Series
- ⚠️ **Highly Variable** - Each model may have different restrictions
- `gpt-5-nano`: Only default temperature (1.0)
- May require `max_completion_tokens` instead of `max_tokens`
- **Recommendation**: Treat as experimental, use fallback pattern

#### O1 and O3 Series
- ❌ **No temperature control** - Fixed by model design
- ✅ Parameter: `max_completion_tokens` (not `max_tokens`)
- 🔧 Designed for reasoning tasks, not creative generation

### Google Gemini Models

#### All Gemini Models
- ✅ Parameter: `max_output_tokens` (in `generation_config`)
- ✅ Temperature: 0.0 - 2.0 (in `generation_config`)
- ⚠️ Response structure varies by library version
- ⚠️ Safety filters can block responses without clear errors
- 📝 Combine system prompt with user prompt (no separate system message)

**Safety Considerations**:
```python
generation_config = {
    'max_output_tokens': max_tokens,
    'temperature': temperature,
    # Optional: Adjust safety settings if needed
    # 'safety_settings': {...}
}
```

### Anthropic Claude

#### All Claude Models
- ✅ Separate `system` parameter (not in messages array)
- ✅ Standard `max_tokens` parameter
- ✅ Temperature: 0.0 - 1.0
- ✅ Very consistent API across models
- 📝 Messages must alternate user/assistant

**Key Difference**:
```python
# Claude uses system parameter separately
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    system="You are a helpful assistant",  # Separate!
    messages=[
        {"role": "user", "content": "Hello"}
    ],
    max_tokens=1000,
    temperature=0.7
)

# Access response
text = response.content[0].text
```

### xAI (Grok)

#### Grok Models
- ✅ OpenAI-compatible API
- ✅ Standard parameters work
- 🔧 Requires custom base_url: `https://api.x.ai/v1`
- 📝 Use OpenAI client with different endpoint

**Setup**:
```python
from openai import OpenAI

xai_client = OpenAI(
    api_key=xai_api_key,
    base_url="https://api.x.ai/v1"
)

# Then use like OpenAI
response = xai_client.chat.completions.create(
    model="grok-3",
    messages=messages,
    max_tokens=max_tokens,
    temperature=temperature
)
```

---

## Implementation Patterns

### Pattern 1: Progressive Fallback Strategy

Try parameters in order of likelihood, falling back gracefully:

```python
def generate_with_fallback(client, model, messages, max_tokens, temperature):
    """
    Progressive fallback for maximum compatibility
    """
    kwargs = {
        'model': model,
        'messages': messages,
        'temperature': temperature
    }
    last_error = None

    # Attempt 1: Standard parameters
    try:
        kwargs['max_tokens'] = max_tokens
        return client.chat.completions.create(**kwargs)
    except Exception as e:
        last_error = e
        error_str = str(e)

        # Attempt 2: Handle temperature restriction
        if 'temperature' in error_str and 'not support' in error_str.lower():
            del kwargs['temperature']
            try:
                return client.chat.completions.create(**kwargs)
            except Exception as e2:
                last_error = e2
                error_str = str(e2)

        # Attempt 3: Try max_completion_tokens
        if 'max_completion_tokens' in error_str:
            del kwargs['max_tokens']
            kwargs['max_completion_tokens'] = max_tokens
            try:
                return client.chat.completions.create(**kwargs)
            except Exception as e3:
                last_error = e3

        # Attempt 4: Remove all token limits
        try:
            kwargs_minimal = {
                'model': model,
                'messages': messages
            }
            return client.chat.completions.create(**kwargs_minimal)
        except Exception as e4:
            last_error = e4

    raise last_error
```

### Pattern 2: Provider-Specific Adapters

Create adapter functions for each provider:

```python
class ProviderAdapter:
    @staticmethod
    async def openai_generate(client, model, system, user, max_tokens, temp):
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
        response = await generate_with_fallback(
            client, model, messages, max_tokens, temp
        )
        return response.choices[0].message.content

    @staticmethod
    async def anthropic_generate(client, model, system, user, max_tokens, temp):
        # Claude-specific handling
        response = client.messages.create(
            model=model,
            system=system,  # Separate parameter!
            messages=[{"role": "user", "content": user}],
            max_tokens=max_tokens,
            temperature=temp
        )
        return response.content[0].text

    @staticmethod
    async def gemini_generate(model_name, system, user, max_tokens, temp):
        model = genai.GenerativeModel(model_name)
        full_prompt = f"{system}\n\n{user}"

        response = model.generate_content(
            full_prompt,
            generation_config={
                'max_output_tokens': max_tokens,
                'temperature': temp
            }
        )

        return extract_gemini_text(response)
```

### Pattern 3: Error Detection and Logging

Implement comprehensive error logging for debugging:

```python
def log_api_call(provider, model, params, error=None):
    """Log API calls for debugging"""
    if error:
        print(f"❌ [{provider}] Error with {model}: {error}")
        # Parse error for specific issues
        error_str = str(error)
        if 'temperature' in error_str:
            print(f"   → Temperature issue detected")
        if 'max_tokens' in error_str or 'max_completion_tokens' in error_str:
            print(f"   → Token parameter issue detected")
    else:
        print(f"✅ [{provider}] Success with {model}")

# Usage in your generation function
try:
    response = client.create(**kwargs)
    log_api_call("OpenAI", model, kwargs)
    return response
except Exception as e:
    log_api_call("OpenAI", model, kwargs, error=e)
    # Continue with fallback logic
```

---

## Testing Strategies

### 1. Parameter Compatibility Matrix

Create a test matrix for each model:

```python
TEST_CASES = [
    # (model, temperature, max_tokens, should_work)
    ("gpt-4o", 0.7, 1000, True),
    ("gpt-5-nano", 0.7, 1000, "fallback_temp"),  # Needs default temp
    ("o1-preview", 0.7, 1000, "fallback_both"),  # Needs both fallbacks
    ("gemini-2.5-flash", 0.7, 1000, True),
]

async def test_model_compatibility(provider, model, temp, max_tokens):
    """Test if model works with given parameters"""
    try:
        response = await generate(
            provider=provider,
            model=model,
            system="Test",
            user="Say hello",
            max_tokens=max_tokens,
            temperature=temp
        )
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Run tests
for model, temp, max_tokens, expected in TEST_CASES:
    result = await test_model_compatibility("openai", model, temp, max_tokens)
    print(f"{model}: {result['status']}")
```

### 2. Response Structure Validation

Test response extraction for each provider:

```python
async def test_response_extraction(provider, model):
    """Ensure we can extract text from response"""
    response = await generate(provider, model, "Test", "Hello", 100, 0.7)

    assert isinstance(response, str), "Response should be string"
    assert len(response) > 0, "Response should not be empty"
    assert not response.startswith("Error"), "Response should not be error"

    print(f"✅ {provider} {model}: {len(response)} chars")
```

### 3. Fallback Chain Testing

Verify fallback logic works correctly:

```python
async def test_fallback_chain(model_config):
    """Test that fallback chain handles all error types"""

    # Test 1: Should work with standard params
    result = await generate_with_fallback(...)
    assert result is not None

    # Test 2: Should handle temperature restriction
    # (Mock or use known restrictive model)

    # Test 3: Should handle token param variation
    # (Mock or use known variant model)

    # Test 4: Should gracefully degrade
    # (Test with invalid params)
```

---

## Code Examples

### Complete Multi-Provider Manager

```python
from typing import Optional, List, Dict
from enum import Enum
import google.generativeai as genai
from anthropic import Anthropic
from openai import OpenAI

class Provider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    XAI = "xai"

class MultiProviderAI:
    def __init__(self):
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            genai.configure(api_key=google_key)

        self.xai = OpenAI(
            api_key=os.getenv("XAI_API_KEY"),
            base_url="https://api.x.ai/v1"
        )

    async def generate(
        self,
        provider: Provider,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> str:
        """
        Universal generate method with automatic compatibility handling
        """
        try:
            if provider == Provider.OPENAI:
                return await self._generate_openai(
                    model, system_prompt, user_prompt, max_tokens, temperature
                )
            elif provider == Provider.ANTHROPIC:
                return await self._generate_anthropic(
                    model, system_prompt, user_prompt, max_tokens, temperature
                )
            elif provider == Provider.GOOGLE:
                return await self._generate_google(
                    model, system_prompt, user_prompt, max_tokens, temperature
                )
            elif provider == Provider.XAI:
                return await self._generate_xai(
                    model, system_prompt, user_prompt, max_tokens, temperature
                )
        except Exception as e:
            print(f"❌ Error with {provider.value} ({model}): {e}")
            raise

    async def _generate_openai(self, model, system, user, max_tokens, temp):
        """OpenAI with full compatibility handling"""
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

        kwargs = {"model": model, "messages": messages, "temperature": temp}
        last_error = None

        # Try standard params
        try:
            kwargs["max_tokens"] = max_tokens
            response = self.openai.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            error_str = str(e)

            # Handle temperature restriction
            if "temperature" in error_str and "not support" in error_str.lower():
                print(f"⚠️ Removing temperature for {model}")
                del kwargs["temperature"]
                try:
                    response = self.openai.chat.completions.create(**kwargs)
                    return response.choices[0].message.content
                except Exception as e2:
                    last_error = e2
                    error_str = str(e2)

            # Handle token param variation
            if "max_completion_tokens" in error_str:
                print(f"⚠️ Using max_completion_tokens for {model}")
                del kwargs["max_tokens"]
                kwargs["max_completion_tokens"] = max_tokens
                try:
                    response = self.openai.chat.completions.create(**kwargs)
                    return response.choices[0].message.content
                except Exception as e3:
                    last_error = e3

            # Last resort: no limits
            try:
                kwargs_minimal = {"model": model, "messages": messages}
                response = self.openai.chat.completions.create(**kwargs_minimal)
                return response.choices[0].message.content
            except Exception as e4:
                last_error = e4

        raise last_error

    async def _generate_anthropic(self, model, system, user, max_tokens, temp):
        """Anthropic Claude"""
        response = self.anthropic.messages.create(
            model=model,
            system=system,
            messages=[{"role": "user", "content": user}],
            max_tokens=max_tokens,
            temperature=temp
        )
        return response.content[0].text

    async def _generate_google(self, model, system, user, max_tokens, temp):
        """Google Gemini with robust extraction"""
        gemini_model = genai.GenerativeModel(model)
        full_prompt = f"{system}\n\n{user}"

        response = gemini_model.generate_content(
            full_prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temp
            }
        )

        # Use robust extraction
        return self._extract_gemini_text(response)

    async def _generate_xai(self, model, system, user, max_tokens, temp):
        """xAI (uses OpenAI-compatible API)"""
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]

        response = self.xai.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temp
        )
        return response.choices[0].message.content

    def _extract_gemini_text(self, response) -> str:
        """Robust Gemini text extraction"""
        if not response.candidates:
            raise Exception("No candidates - blocked by safety filters")

        candidate = response.candidates[0]

        # Check safety
        if hasattr(candidate, 'finish_reason'):
            if 'SAFETY' in str(candidate.finish_reason):
                raise Exception(f"Blocked: {candidate.finish_reason}")

        # Try parts extraction
        if candidate.content and candidate.content.parts:
            text_parts = []
            for part in candidate.content.parts:
                if hasattr(part, 'text') and part.text:
                    text_parts.append(part.text)
            if text_parts:
                return ''.join(text_parts)

        # Try direct accessors
        try:
            if response.text:
                return response.text
        except:
            pass

        try:
            if candidate.text:
                return candidate.text
        except:
            pass

        raise Exception("Could not extract text from Gemini response")
```

---

## Best Practices Summary

### ✅ DO:

1. **Always implement fallback chains** for parameter compatibility
2. **Log errors with context** to understand model behavior
3. **Test with actual models** - mocking misses compatibility issues
4. **Handle edge cases gracefully** - return to defaults when possible
5. **Document model-specific quirks** as you discover them
6. **Version your provider libraries** and document known working versions

### ❌ DON'T:

1. **Assume consistency** across models in the same family
2. **Hard-code parameter values** - make everything configurable
3. **Ignore library version** - API and SDK can be out of sync
4. **Skip error logging** - errors contain valuable compatibility info
5. **Retry indefinitely** - have a clear failure path
6. **Use silent fallbacks** without logging - makes debugging impossible

---

## Quick Reference

### Parameter Compatibility Quick Check

```python
# OpenAI Models
if model.startswith('gpt-5-nano'):
    temperature = None  # Use default only
    max_tokens_param = 'max_tokens'  # Usually
elif model.startswith('o1') or model.startswith('o3'):
    temperature = None  # Not supported
    max_tokens_param = 'max_completion_tokens'
else:  # gpt-3.5, gpt-4
    temperature = 0.0 to 2.0
    max_tokens_param = 'max_tokens'

# Google Gemini
temperature = 0.0 to 2.0
max_tokens_param = 'max_output_tokens'  # In generation_config

# Anthropic Claude
temperature = 0.0 to 1.0
max_tokens_param = 'max_tokens'
# Note: system prompt is separate parameter

# xAI Grok
temperature = 0.0 to 2.0
max_tokens_param = 'max_tokens'
# Note: requires base_url="https://api.x.ai/v1"
```

---

## Appendix: Library Versions Used in Testing

```
anthropic==0.18.1
openai==1.12.0
google-generativeai==0.3.2
```

**Note**: Newer versions may have different behaviors. Always test with your specific versions.

---

## Contributing

Found a new compatibility issue? Document it with:
1. Provider and model name
2. Error message
3. Working solution
4. Library versions

This guide is a living document - update as you discover new patterns!

---

**Document Version**: 1.0
**Last Updated**: 2025-11-08
**Maintainer**: AI Learning Project Team
