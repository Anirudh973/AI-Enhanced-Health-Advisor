from __future__ import annotations as _annotations

from dataclasses import dataclass
from dotenv import load_dotenv
import logfire
import asyncio
import httpx
import os

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncOpenAI
from supabase import Client
from typing import List

load_dotenv()

llm = os.getenv('LLM_MODEL', 'gpt-4o-mini')
model = OpenAIModel(llm)

logfire.configure(send_to_logfire='if-token-present')

@dataclass
class NHSHealthDeps:
    supabase: Client
    openai_client: AsyncOpenAI

system_prompt = """
You are the NHS Health Advisor AI, an expert at analyzing symptoms and providing healthcare information based on official NHS guidelines. Your primary responsibilities are:

1. Analyze user symptoms carefully and thoroughly
2. Match symptoms with potential conditions from the NHS database
3. Provide detailed information about identified conditions
4. Suggest appropriate next steps and when to seek medical attention
5. Include relevant NHS treatment guidelines when applicable

IMPORTANT MEDICAL DISCLAIMER: Always begin your responses with:
"🏥 NHS Health Advisory Notice: This information is for general guidance only and should not replace professional medical advice. If you have severe symptoms or are concerned, please contact NHS 111, visit your GP, or call 999 in emergencies."

When analyzing symptoms:
- Ask follow-up questions if symptoms are vague
- Consider multiple possible conditions
- Highlight any red flags that require immediate medical attention
- Provide reliable NHS-sourced information about management and treatment
- Include links to relevant NHS condition pages when available

Remember: You are not making diagnoses, but rather providing NHS-guided information to help users understand their health concerns better.
"""

nhs_health_advisor = Agent(
    model,
    system_prompt=system_prompt,
    deps_type=NHSHealthDeps,
    retries=2
)

async def get_embedding(text: str, openai_client: AsyncOpenAI) -> List[float]:
    """Get embedding vector from OpenAI."""
    try:
        response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536

@nhs_health_advisor.tool
async def analyze_symptoms(ctx: RunContext[NHSHealthDeps], symptoms: str) -> str:
    """
    Analyze user symptoms and retrieve relevant NHS condition information.
    
    Args:
        ctx: The context including the Supabase client and OpenAI client
        symptoms: The user's described symptoms
        
    Returns:
        A formatted response with potential conditions and advice
    """
    try:
        query_embedding = await get_embedding(symptoms, ctx.deps.openai_client)
        
        # Query Supabase for relevant conditions
        result = ctx.deps.supabase.rpc(
            'match_site_pages',
            {
                'query_embedding': query_embedding,
                'match_count': 5,
                'filter': {'source': 'nhs_conditions'}
            }
        ).execute()
        
        if not result.data:
            return "I couldn't find any relevant NHS information for your symptoms. Please contact NHS 111 for guidance."
            
        # Format the results with clear sections
        formatted_response = ["🏥 NHS Health Advisory Notice: This information is for general guidance only and should not replace professional medical advice. If you have severe symptoms or are concerned, please contact NHS 111, visit your GP, or call 999 in emergencies.\n"]
        
        formatted_response.append("\n## Potential Related Conditions:\n")
        
        for doc in result.data:
            formatted_response.append(f"""
### {doc['title']}

{doc['content']}

🔗 More information: {doc['url']}
""")
            
        formatted_response.append("\n## When to Seek Medical Help:\n")
        formatted_response.append("Contact NHS 111 or your GP if:")
        formatted_response.append("- Your symptoms persist or worsen")
        formatted_response.append("- You're unsure about the severity of your condition")
        formatted_response.append("- You need more specific medical advice")
        
        return "\n".join(formatted_response)
        
    except Exception as e:
        print(f"Error analyzing symptoms: {e}")
        return "I apologize, but I encountered an error while analyzing your symptoms. Please contact NHS 111 for assistance."

@nhs_health_advisor.tool
async def get_condition_info(ctx: RunContext[NHSHealthDeps], condition: str) -> str:
    """
    Retrieve detailed information about a specific health condition from NHS resources.
    
    Args:
        ctx: The context including the Supabase client
        condition: The specific condition to look up
        
    Returns:
        Detailed information about the condition from NHS sources
    """
    try:
        query_embedding = await get_embedding(condition, ctx.deps.openai_client)
        
        result = ctx.deps.supabase.rpc(
            'match_site_pages',
            {
                'query_embedding': query_embedding,
                'match_count': 1,
                'filter': {'source': 'nhs_conditions'}
            }
        ).execute()
        
        if not result.data:
            return f"No NHS information found for condition: {condition}"
            
        doc = result.data[0]
        return f"""
# {doc['title']}

{doc['content']}

🔗 Source: {doc['url']}

Remember: This information is from the NHS website and is for general guidance only. Always consult healthcare professionals for specific medical advice.
"""
        
    except Exception as e:
        print(f"Error retrieving condition info: {e}")
        return f"Error retrieving NHS information for: {condition}"