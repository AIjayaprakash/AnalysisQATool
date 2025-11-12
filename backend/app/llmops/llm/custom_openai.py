"""Custom OpenAI LLM wrapper for LangChain compatibility with custom gateway"""

from typing import List, Optional, Any
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import LLMResult, Generation
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from openai import OpenAI


class CustomOpenAILLM(LLM):
    """
    Custom LLM wrapper for OpenAI gateway that works with LangChain tools and agents.
    Supports custom gateway URLs and headers for enterprise deployments.
    """
    
    api_key: str = "placeholder-key"
    model: str = "gpt-4o"
    gateway_url: str = None
    client: Any = None
    
    def __init__(
        self, 
        api_key: str = "placeholder-key", 
        model: str = "gpt-4o", 
        gateway_url: str = None,
        **kwargs
    ):
        """
        Initialize Custom OpenAI LLM
        
        Args:
            api_key: API key for authentication
            model: Model name (e.g., gpt-4o)
            gateway_url: Custom gateway URL (if None, uses default pattern)
            **kwargs: Additional LangChain LLM arguments
        """
        super().__init__(**kwargs)
        self.api_key = api_key or "placeholder-key"
        self.model = model
        
        if gateway_url:
            self.gateway_url = gateway_url
        else:
            # Use default gateway URL pattern
            self.gateway_url = f"https://gateway.ai-npe.humana.com/openai/deployments/{model}"
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=self.gateway_url,
        )
        
        print(f"[INFO] Custom OpenAI LLM initialized:")
        print(f"  Model: {self.model}")
        print(f"  Gateway URL: {self.gateway_url}")
    
    @property
    def _llm_type(self) -> str:
        """Return LLM type identifier"""
        return "custom_openai_gateway"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        """
        Call the custom OpenAI gateway with a prompt
        
        Args:
            prompt: Input prompt string
            stop: Optional stop sequences
            **kwargs: Additional arguments
        
        Returns:
            Generated text response
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                extra_headers={
                    "api-key": self.api_key, 
                    "ai-gateway-version": "v2"
                },
            )
            
            return chat_completion.choices[0].message.content
            
        except Exception as e:
            print(f"[ERROR] Custom OpenAI LLM error: {e}")
            return f"Error calling custom OpenAI LLM: {str(e)}"
    
    def _generate(
        self, 
        prompts: List[str], 
        stop: Optional[List[str]] = None, 
        **kwargs
    ) -> LLMResult:
        """
        Generate responses for multiple prompts
        
        Args:
            prompts: List of input prompts
            stop: Optional stop sequences
            **kwargs: Additional arguments
        
        Returns:
            LLMResult with generations
        """
        generations = []
        for prompt in prompts:
            response = self._call(prompt, stop=stop, **kwargs)
            generations.append([Generation(text=response)])
        
        return LLMResult(generations=generations)
    
    def invoke(self, messages: List[BaseMessage]) -> AIMessage:
        """
        Invoke with LangChain messages - returns AIMessage for compatibility
        
        Args:
            messages: List of LangChain BaseMessage objects
        
        Returns:
            AIMessage with response content
        """
        # Convert LangChain messages to OpenAI format
        openai_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                openai_messages.append({"role": "user", "content": str(msg.content)})
            elif isinstance(msg, AIMessage):
                openai_messages.append({"role": "assistant", "content": str(msg.content)})
            elif isinstance(msg, SystemMessage):
                openai_messages.append({"role": "system", "content": str(msg.content)})
            else:
                openai_messages.append({"role": "user", "content": str(msg.content)})
        
        print(f"[DEBUG] Sending {len(openai_messages)} messages to custom OpenAI gateway")
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=openai_messages,
                model=self.model,
                extra_headers={
                    "api-key": self.api_key, 
                    "ai-gateway-version": "v2"
                },
            )
            
            response_content = chat_completion.choices[0].message.content
            print(f"[DEBUG] Received response from custom OpenAI gateway: {len(response_content)} chars")
            
            # Return proper AIMessage for LangChain compatibility
            return AIMessage(content=response_content)
            
        except Exception as e:
            print(f"[ERROR] Custom OpenAI LLM error: {e}")
            return AIMessage(content=f"Error calling custom OpenAI LLM: {str(e)}")
