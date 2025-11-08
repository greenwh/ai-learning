"""
AI Provider Manager - Handles multiple AI providers with fallback support
"""
from typing import Dict, List, Optional, Any
from enum import Enum
import os
from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai


class AIProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    XAI = "xai"


class TaskType(Enum):
    CONTENT_GENERATION = "content_generation"
    TUTOR_RESPONSE = "tutor_response"
    QUICK_QA = "quick_qa"
    VISUAL_DESCRIPTION = "visual_description"
    COMPREHENSION_CHECK = "comprehension_check"


class AIProviderManager:
    """
    Manages multiple AI providers and selects the best one for each task
    """

    def __init__(self):
        # Initialize providers
        self.anthropic_client = None
        self.openai_client = None
        self.google_configured = False
        self.xai_client = None

        # Configure Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key:
            self.anthropic_client = Anthropic(api_key=anthropic_key)
            self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

        # Configure OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
            self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # Configure Google
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            genai.configure(api_key=google_key)
            self.google_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
            self.google_configured = True

        # Configure xAI (uses OpenAI-compatible API)
        xai_key = os.getenv("XAI_API_KEY")
        if xai_key:
            self.xai_client = OpenAI(
                api_key=xai_key,
                base_url="https://api.x.ai/v1"
            )
            self.xai_model = os.getenv("XAI_MODEL", "grok-3")

    def select_provider(
        self,
        task_type: TaskType,
        user_preference: Optional[AIProvider] = None
    ) -> AIProvider:
        """
        Select the best AI provider for the given task type

        Args:
            task_type: The type of task to perform
            user_preference: Optional user preference for provider

        Returns:
            The selected AI provider
        """
        if user_preference and self._is_provider_available(user_preference):
            print(f"🤖 [AI Provider] Using user preference: {user_preference.value}")
            return user_preference

        # Task-based provider selection
        selected_provider = None

        if task_type == TaskType.CONTENT_GENERATION:
            # Claude excels at educational content
            if self.anthropic_client:
                selected_provider = AIProvider.ANTHROPIC

        elif task_type == TaskType.QUICK_QA:
            # Fast models for rapid Q&A
            if self.openai_client:
                selected_provider = AIProvider.OPENAI

        elif task_type == TaskType.VISUAL_DESCRIPTION:
            # Gemini good at visual reasoning
            if self.google_configured:
                selected_provider = AIProvider.GOOGLE

        elif task_type == TaskType.TUTOR_RESPONSE:
            # Claude for conversational tutoring
            if self.anthropic_client:
                selected_provider = AIProvider.ANTHROPIC

        # Fallback to first available provider if no task-specific selection made
        if not selected_provider:
            if self.anthropic_client:
                selected_provider = AIProvider.ANTHROPIC
            elif self.openai_client:
                selected_provider = AIProvider.OPENAI
            elif self.xai_client:
                selected_provider = AIProvider.XAI
            elif self.google_configured:
                selected_provider = AIProvider.GOOGLE

        if not selected_provider:
            raise ValueError("No AI provider configured")

        print(f"🤖 [AI Provider] Selected {selected_provider.value} for {task_type.value}")
        return selected_provider

    def _is_provider_available(self, provider: AIProvider) -> bool:
        """Check if a provider is available"""
        if provider == AIProvider.ANTHROPIC:
            return self.anthropic_client is not None
        elif provider == AIProvider.OPENAI:
            return self.openai_client is not None
        elif provider == AIProvider.GOOGLE:
            return self.google_configured
        elif provider == AIProvider.XAI:
            return self.xai_client is not None
        return False

    async def generate_content(
        self,
        provider: AIProvider,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate content using the specified provider

        Args:
            provider: AI provider to use
            system_prompt: System prompt/instructions
            user_prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            conversation_history: Optional conversation history

        Returns:
            Generated content as string
        """
        # Get model name for logging
        model_name = "unknown"
        if provider == AIProvider.ANTHROPIC:
            model_name = self.anthropic_model
        elif provider == AIProvider.OPENAI:
            model_name = self.openai_model
        elif provider == AIProvider.GOOGLE:
            model_name = self.google_model
        elif provider == AIProvider.XAI:
            model_name = self.xai_model

        print(f"📤 [AI API Call] Sending to {provider.value} ({model_name})")

        try:
            if provider == AIProvider.ANTHROPIC:
                return await self._generate_anthropic(
                    system_prompt, user_prompt, max_tokens,
                    temperature, conversation_history
                )
            elif provider == AIProvider.OPENAI:
                return await self._generate_openai(
                    system_prompt, user_prompt, max_tokens,
                    temperature, conversation_history
                )
            elif provider == AIProvider.GOOGLE:
                return await self._generate_google(
                    system_prompt, user_prompt, max_tokens,
                    temperature, conversation_history
                )
            elif provider == AIProvider.XAI:
                return await self._generate_xai(
                    system_prompt, user_prompt, max_tokens,
                    temperature, conversation_history
                )
            else:
                raise ValueError(f"Unknown provider: {provider}")

        except Exception as e:
            print(f"❌ [AI API Error] Error with {provider.value} ({model_name}): {e}")
            # Try fallback provider
            return await self._generate_with_fallback(
                provider, system_prompt, user_prompt,
                max_tokens, temperature, conversation_history
            )

    async def _generate_anthropic(
        self, system_prompt: str, user_prompt: str,
        max_tokens: int, temperature: float,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate content using Anthropic Claude"""
        messages = []

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user prompt
        messages.append({"role": "user", "content": user_prompt})

        response = self.anthropic_client.messages.create(
            model=self.anthropic_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=messages
        )

        return response.content[0].text

    async def _generate_openai(
        self, system_prompt: str, user_prompt: str,
        max_tokens: int, temperature: float,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate content using OpenAI"""
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user prompt
        messages.append({"role": "user", "content": user_prompt})

        kwargs = {
            "model": self.openai_model,
            "messages": messages,
            "temperature": temperature
        }

        # Try different token parameter approaches based on model
        # Some models use max_completion_tokens, some use max_tokens
        # The API and Python library versions may have different support
        model_lower = self.openai_model.lower()

        # First, try with the parameter that should work based on model type
        if model_lower.startswith('o1') or model_lower.startswith('o3'):
            # o1/o3 models definitely use max_completion_tokens
            try:
                kwargs["max_completion_tokens"] = max_tokens
                response = self.openai_client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except TypeError:
                # Python library doesn't support this parameter yet
                del kwargs["max_completion_tokens"]

        # For all other models (including gpt-5, gpt-4, etc.), try max_tokens first
        # We'll try multiple combinations to handle different model restrictions
        last_error = None

        # Attempt 1: Try with temperature + max_tokens (the ideal case)
        try:
            kwargs["max_tokens"] = max_tokens
            response = self.openai_client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            error_str = str(e)

            # Check if temperature is the issue
            if "temperature" in error_str and ("not support" in error_str or "unsupported" in error_str.lower()):
                print(f"⚠️ [OpenAI] Model {self.openai_model} doesn't support custom temperature, using default")
                # Attempt 2: Remove temperature and retry
                if "temperature" in kwargs:
                    del kwargs["temperature"]

                try:
                    response = self.openai_client.chat.completions.create(**kwargs)
                    return response.choices[0].message.content
                except Exception as e2:
                    last_error = e2
                    error_str = str(e2)

            # Check if we need max_completion_tokens instead of max_tokens
            if "max_completion_tokens" in error_str:
                print(f"⚠️ [OpenAI] Model {self.openai_model} requires max_completion_tokens instead of max_tokens")
                # Attempt 3: Try max_completion_tokens
                try:
                    if "max_tokens" in kwargs:
                        del kwargs["max_tokens"]
                    kwargs["max_completion_tokens"] = max_tokens
                    response = self.openai_client.chat.completions.create(**kwargs)
                    return response.choices[0].message.content
                except Exception as e3:
                    last_error = e3

            # Attempt 4: Last resort - try without any token limit
            try:
                if "max_tokens" in kwargs:
                    del kwargs["max_tokens"]
                if "max_completion_tokens" in kwargs:
                    del kwargs["max_completion_tokens"]
                print(f"⚠️ [OpenAI] Trying without token limit for model {self.openai_model}")
                response = self.openai_client.chat.completions.create(**kwargs)
                return response.choices[0].message.content
            except Exception as e4:
                last_error = e4

            # If all attempts failed, raise the last error
            raise last_error

    async def _generate_google(
        self, system_prompt: str, user_prompt: str,
        max_tokens: int, temperature: float,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate content using Google Gemini"""
        model = genai.GenerativeModel(self.google_model)

        # Combine system prompt with user prompt for Gemini
        full_prompt = f"{system_prompt}\n\n{user_prompt}"

        # Add conversation history if provided
        if conversation_history:
            history_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history
            ])
            full_prompt = f"{history_text}\n\n{full_prompt}"

        response = model.generate_content(
            full_prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature
            }
        )

        # Handle response properly - check for blocking or use parts accessor
        if not response.candidates:
            raise Exception("Gemini returned no candidates - response may have been blocked by safety filters")

        candidate = response.candidates[0]

        # Check for blocked content
        if hasattr(candidate, 'finish_reason'):
            finish_reason = str(candidate.finish_reason)
            if 'SAFETY' in finish_reason or 'BLOCKED' in finish_reason:
                raise Exception(f"Gemini response blocked due to safety filters: {finish_reason}")

        # Try multiple methods to extract text
        print(f"🔍 [Gemini Debug] Processing response with {len(response.candidates)} candidate(s)")

        # Method 1: Extract text from parts (most reliable for newer API versions)
        try:
            if candidate.content and candidate.content.parts is not None:
                parts_list = list(candidate.content.parts)
                print(f"🔍 [Gemini Debug] Found {len(parts_list)} part(s) in candidate.content.parts")

                text_parts = []
                for i, part in enumerate(parts_list):
                    print(f"🔍 [Gemini Debug] Part {i}: type={type(part).__name__}, has_text={hasattr(part, 'text')}")

                    # Try different ways to get text from the part
                    part_text = None

                    # Direct attribute access
                    if hasattr(part, 'text'):
                        try:
                            part_text = part.text
                            print(f"🔍 [Gemini Debug] Part {i}: got text via attribute, length={len(str(part_text)) if part_text else 0}")
                        except Exception as e:
                            print(f"⚠️ [Gemini Debug] Part {i}: attribute access failed: {e}")

                    # Try as dictionary (some versions return dict-like objects)
                    if not part_text and isinstance(part, dict) and 'text' in part:
                        part_text = part['text']
                        print(f"🔍 [Gemini Debug] Part {i}: got text via dict access")

                    # Try callable
                    if not part_text and callable(getattr(part, 'text', None)):
                        try:
                            part_text = part.text()
                            print(f"🔍 [Gemini Debug] Part {i}: got text via callable")
                        except Exception as e:
                            print(f"⚠️ [Gemini Debug] Part {i}: callable access failed: {e}")

                    if part_text:
                        text_parts.append(str(part_text))

                if text_parts:
                    result = ''.join(text_parts)
                    print(f"✅ [Gemini Debug] Extracted {len(result)} chars from {len(text_parts)} part(s)")
                    return result
                else:
                    print(f"⚠️ [Gemini Debug] Method 1 failed: parts exist but no text extracted")
        except Exception as e:
            print(f"⚠️ [Gemini Debug] Method 1 (candidate.content.parts) failed: {e}")

        # Method 2: Try direct text accessor on response
        try:
            text = response.text
            if text:
                print(f"✅ [Gemini Debug] Extracted {len(text)} chars from response.text")
                return text
        except Exception as e:
            print(f"⚠️ [Gemini Debug] response.text failed: {e}")

        # Method 3: Try to access text from candidate directly
        try:
            if hasattr(candidate, 'text'):
                text = candidate.text
                if text:
                    print(f"✅ [Gemini Debug] Extracted {len(text)} chars from candidate.text")
                    return text
        except Exception as e:
            print(f"⚠️ [Gemini Debug] candidate.text failed: {e}")

        # Method 4: Try accessing the raw response parts differently
        try:
            if hasattr(response, 'parts') and response.parts:
                text_parts = []
                for part in response.parts:
                    if hasattr(part, 'text'):
                        text_parts.append(str(part.text))

                if text_parts:
                    result = ''.join(text_parts)
                    print(f"✅ [Gemini Debug] Extracted {len(result)} chars from response.parts")
                    return result
        except Exception as e:
            print(f"⚠️ [Gemini Debug] response.parts failed: {e}")

        # If all methods fail, provide detailed error
        error_details = f"Could not extract text from Gemini response. "
        error_details += f"Candidates: {len(response.candidates) if response.candidates else 0}, "

        if candidate:
            error_details += f"Finish reason: {candidate.finish_reason if hasattr(candidate, 'finish_reason') else 'unknown'}, "
            error_details += f"Has content: {candidate.content is not None}, "

            if candidate.content:
                error_details += f"Has parts: {candidate.content.parts is not None}, "

                if candidate.content.parts is not None:
                    try:
                        parts_count = len(list(candidate.content.parts))
                        error_details += f"Parts count: {parts_count}, "
                        # Try to get part types for debugging
                        part_types = [type(p).__name__ for p in candidate.content.parts]
                        error_details += f"Part types: {part_types}, "

                        # Try to see what attributes parts have
                        if parts_count > 0:
                            first_part = list(candidate.content.parts)[0]
                            part_attrs = [attr for attr in dir(first_part) if not attr.startswith('_')]
                            error_details += f"First part attributes: {part_attrs[:10]}"  # Limit to first 10
                    except Exception as e:
                        error_details += f"Error inspecting parts: {e}"

        print(f"❌ [Gemini Debug] {error_details}")
        raise Exception(error_details)

    async def _generate_xai(
        self, system_prompt: str, user_prompt: str,
        max_tokens: int, temperature: float,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate content using xAI (Grok) - uses OpenAI-compatible API"""
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user prompt
        messages.append({"role": "user", "content": user_prompt})

        # xAI uses standard OpenAI API format
        response = self.xai_client.chat.completions.create(
            model=self.xai_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content

    async def _generate_with_fallback(
        self, failed_provider: AIProvider, system_prompt: str,
        user_prompt: str, max_tokens: int, temperature: float,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Try to generate with fallback provider"""
        fallback_order = [
            AIProvider.ANTHROPIC,
            AIProvider.OPENAI,
            AIProvider.XAI,
            AIProvider.GOOGLE
        ]

        for provider in fallback_order:
            if provider != failed_provider and self._is_provider_available(provider):
                try:
                    if provider == AIProvider.ANTHROPIC:
                        return await self._generate_anthropic(
                            system_prompt, user_prompt, max_tokens,
                            temperature, conversation_history
                        )
                    elif provider == AIProvider.OPENAI:
                        return await self._generate_openai(
                            system_prompt, user_prompt, max_tokens,
                            temperature, conversation_history
                        )
                    elif provider == AIProvider.XAI:
                        return await self._generate_xai(
                            system_prompt, user_prompt, max_tokens,
                            temperature, conversation_history
                        )
                    elif provider == AIProvider.GOOGLE:
                        return await self._generate_google(
                            system_prompt, user_prompt, max_tokens,
                            temperature, conversation_history
                        )
                except Exception as e:
                    print(f"Fallback provider {provider} also failed: {e}")
                    continue

        raise Exception("All AI providers failed")


# Global instance
ai_provider_manager = AIProviderManager()
