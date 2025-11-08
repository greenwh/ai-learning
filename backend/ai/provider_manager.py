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
            return user_preference

        # Task-based provider selection
        if task_type == TaskType.CONTENT_GENERATION:
            # Claude excels at educational content
            if self.anthropic_client:
                return AIProvider.ANTHROPIC

        elif task_type == TaskType.QUICK_QA:
            # Fast models for rapid Q&A
            if self.openai_client:
                return AIProvider.OPENAI

        elif task_type == TaskType.VISUAL_DESCRIPTION:
            # Gemini good at visual reasoning
            if self.google_configured:
                return AIProvider.GOOGLE

        elif task_type == TaskType.TUTOR_RESPONSE:
            # Claude for conversational tutoring
            if self.anthropic_client:
                return AIProvider.ANTHROPIC

        # Fallback to first available provider
        if self.anthropic_client:
            return AIProvider.ANTHROPIC
        elif self.openai_client:
            return AIProvider.OPENAI
        elif self.google_configured:
            return AIProvider.GOOGLE

        raise ValueError("No AI provider configured")

    def _is_provider_available(self, provider: AIProvider) -> bool:
        """Check if a provider is available"""
        if provider == AIProvider.ANTHROPIC:
            return self.anthropic_client is not None
        elif provider == AIProvider.OPENAI:
            return self.openai_client is not None
        elif provider == AIProvider.GOOGLE:
            return self.google_configured
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
            else:
                raise ValueError(f"Unknown provider: {provider}")

        except Exception as e:
            print(f"Error generating content with {provider}: {e}")
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

        response = self.openai_client.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

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

        return response.text

    async def _generate_with_fallback(
        self, failed_provider: AIProvider, system_prompt: str,
        user_prompt: str, max_tokens: int, temperature: float,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Try to generate with fallback provider"""
        fallback_order = [
            AIProvider.ANTHROPIC,
            AIProvider.OPENAI,
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
