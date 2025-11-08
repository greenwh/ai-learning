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

        # Newer models use max_completion_tokens instead of max_tokens
        # This includes: o1, o3, and gpt-5 series models
        model_lower = self.openai_model.lower()
        uses_new_api = (
            model_lower.startswith('o1') or
            model_lower.startswith('o3') or
            model_lower.startswith('gpt-5')
        )

        kwargs = {
            "model": self.openai_model,
            "messages": messages,
            "temperature": temperature
        }

        # Use appropriate token parameter
        if uses_new_api:
            kwargs["max_completion_tokens"] = max_tokens
        else:
            kwargs["max_tokens"] = max_tokens

        response = self.openai_client.chat.completions.create(**kwargs)

        return response.choices[0].message.content

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
            raise Exception("Gemini returned no candidates")

        candidate = response.candidates[0]

        # Extract text from parts
        if candidate.content and candidate.content.parts:
            text_parts = [part.text for part in candidate.content.parts if hasattr(part, 'text')]
            return ''.join(text_parts)

        # Fallback to simple text accessor if it works
        try:
            return response.text
        except:
            raise Exception("Could not extract text from Gemini response")

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
