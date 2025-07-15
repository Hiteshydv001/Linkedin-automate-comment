"""
Text processing utilities for OpenVoiceOS engine.

This module provides various text processing functions used throughout the engine,
including text cleaning, normalization, and formatting utilities.
"""
import re
import json
import logging
from typing import Dict, List, Optional, Union, Any
from urllib.parse import quote

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespace, normalizing quotes, etc.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Normalize whitespace and clean up
    text = ' '.join(text.split())
    
    # Normalize quotes
    text = text.replace('"', "''").replace('`', "'").replace('"', "'")
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Normalize unicode
    try:
        import unicodedata
        text = unicodedata.normalize('NFKC', text)
    except Exception as e:
        logger.warning(f"Error normalizing unicode: {e}")
    
    return text.strip()

def format_messages(messages: List[Dict[str, str]], include_tools: bool = False) -> str:
    """
    Format a list of message dictionaries into a single string.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        include_tools: Whether to include tool calls in the formatted output
        
    Returns:
        Formatted string representation of messages
    """
    if not messages:
        return ""
        
    formatted = []
    for msg in messages:
        role = msg.get('role', 'user').capitalize()
        content = msg.get('content', '')
        
        if include_tools and 'tool_calls' in msg and msg['tool_calls']:
            tool_calls = msg['tool_calls']
            if isinstance(tool_calls, list):
                tool_str = ", ".join([f"{t.get('function', {}).get('name', 'unknown')}" 
                                    for t in tool_calls if t.get('function')])
                if tool_str:
                    content = f"{content} [Called tools: {tool_str}]"
        
        if content:
            formatted.append(f"{role}: {content}")
    
    return "\n".join(formatted)

def clean_json_string(json_str: str) -> Union[Dict, str]:
    """
    Clean and parse a JSON string, handling common formatting issues.
    
    Args:
        json_str: Potentially malformed JSON string
        
    Returns:
        Parsed JSON as dict, or original string if parsing fails
    """
    if not json_str or not isinstance(json_str, str):
        return {}
    
    # Common JSON fixes
    json_str = json_str.strip()
    
    # Handle common JSON formatting issues
    if not (json_str.startswith('{') and json_str.endswith('}')):
        # Try to find JSON object in text
        match = re.search(r'\{.*\}', json_str, re.DOTALL)
        if match:
            json_str = match.group(0)
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error: {e}")
        # Try to fix common JSON issues and retry
        try:
            # Fix common issues like unescaped quotes
            json_str = json_str.replace('\n', ' ').replace('\r', '')
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)  # Trailing commas
            json_str = re.sub(r'([{\[,])\s*([}\],])', r'\1null\2', json_str)  # Missing values
            return json.loads(json_str)
        except Exception:
            logger.warning("Failed to fix JSON, returning as text")
            return json_str

def update_prompt_with_context(prompt: str, context: Dict[str, Any]) -> str:
    """
    Update a prompt string by replacing placeholders with values from context.
    
    Args:
        prompt: The template string with {placeholders}
        context: Dictionary of placeholder-value mappings
        
    Returns:
        String with placeholders replaced by context values
    """
    if not prompt or not context:
        return prompt or ""
    
    try:
        return prompt.format(**context)
    except (KeyError, ValueError) as e:
        logger.warning(f"Error formatting prompt with context: {e}")
        return prompt

def truncate_text(text: str, max_length: int = 1000, ellipsis: str = "...") -> str:
    """
    Truncate text to a maximum length, preserving word boundaries.
    
    Args:
        text: Input text to truncate
        max_length: Maximum length of the output string
        ellipsis: String to append when truncating
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if not text or len(text) <= max_length:
        return text or ""
    
    # Find the last space before max_length
    truncated = text[:max_length - len(ellipsis)]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return f"{truncated}{ellipsis}"

def extract_urls(text: str) -> List[str]:
    """
    Extract all URLs from a text string.
    
    Args:
        text: Input text containing URLs
        
    Returns:
        List of found URLs
    """
    if not text:
        return []
    
    # Simple URL regex - matches most common URL patterns
    url_pattern = r'https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)'
    return re.findall(url_pattern, text)

def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Count the number of tokens in a text string.
    
    Args:
        text: Input text
        encoding_name: The encoding to use (default: cl100k_base used by GPT-4)
        
    Returns:
        Number of tokens
    """
    try:
        import tiktoken
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(text))
    except ImportError:
        # Fallback: approximate token count as 4 chars per token
        return max(1, len(text) // 4)

def is_valid_email(email: str) -> bool:
    """Check if a string is a valid email address."""
    if not email:
        return False
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def is_valid_phone(phone: str) -> bool:
    """Check if a string is a valid phone number."""
    if not phone:
        return False
    # Simple phone number validation - matches most common formats
    return bool(re.match(r'^\+?[0-9\s\-\(\)]{6,}$', phone))

def escape_markdown(text: str) -> str:
    """
    Escape markdown special characters in a string.
    
    Args:
        text: Input text that may contain markdown
        
    Returns:
        Text with markdown special characters escaped
    """
    if not text:
        return ""
    
    # List of markdown special characters to escape
    markdown_chars = r'\`*_{}[]()#+-.!|'
    
    # Add backslash before each special character
    for char in markdown_chars:
        text = text.replace(char, f'\\{char}')
    
    return text