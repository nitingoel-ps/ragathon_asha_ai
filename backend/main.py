import os
import nest_asyncio
import asyncio
from app import HealthCareAgent

nest_asyncio.apply()

# Set up environment variables
from arize.otel import register

tracer_provider = register(
    space_id = "U3BhY2U6MjA2MTQ6emRLRQ==", # in app space settings page
    api_key = "ak-b627c915-01f8-463c-a610-821896dd6eac-JkuxcP1mo4DcZwxTA8e7OKmSmVvKctSm", # in app space settings page
    project_name="agents"
)

from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
OpenAIAgentsInstrumentor().instrument(tracer_provider=tracer_provider)



async def main():
    # Initialize the healthcare agent
    healthcare_agent = HealthCareAgent()
    
    # Run the patient review
    result = await healthcare_agent.review_patient()
    
    # Print results
    #print("Final Output:")
    #print(result["final_output"])
    #print("\nMessage History:")
    #print(result["message_history"])

if __name__ == "__main__":
    asyncio.run(main())
