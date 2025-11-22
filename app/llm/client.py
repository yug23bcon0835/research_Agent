"""Groq LLM client for Qwen model."""

import asyncio
from typing import Dict, List, Optional, Any
from groq import AsyncGroq
from app.config import settings


class GroqClient:
    """Async Groq client for Qwen model interactions."""
    
    def __init__(self):
        self.client: Optional[AsyncGroq] = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the Groq client."""
        try:
            self.client = AsyncGroq(api_key=settings.groq_api_key)
            self._initialized = True
            return True
        except Exception:
            return False
    
    def _ensure_initialized(self):
        """Ensure client is initialized."""
        if not self._initialized or not self.client:
            raise RuntimeError("Groq client not initialized. Call initialize() first.")
    
    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
        timeout: int = 30
    ) -> str:
        """Generate a response from the LLM."""
        self._ensure_initialized()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=settings.groq_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                ),
                timeout=timeout
            )
            
            return response.choices[0].message.content or ""
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"LLM request timed out after {timeout} seconds")
        except Exception as e:
            raise RuntimeError(f"Error generating LLM response: {str(e)}")
    
    async def generate_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """Generate a structured JSON response from the LLM."""
        self._ensure_initialized()
        
        # Add JSON formatting instructions to the prompt
        json_prompt = f"""
{prompt}

Please respond with a valid JSON object. Your response should be properly formatted JSON that can be parsed.
"""
        
        response_text = await self.generate_response(
            prompt=json_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            timeout=timeout
        )
        
        try:
            import json
            # Extract JSON from response if it contains extra text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # If no JSON structure found, return as plain text
                return {"response": response_text}
                
        except json.JSONDecodeError as e:
            # Return the raw response if JSON parsing fails
            return {"response": response_text, "parse_error": str(e)}


# Global LLM client instance
llm_client = GroqClient()
