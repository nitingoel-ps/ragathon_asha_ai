import os
import nest_asyncio
import json
from typing import Optional, List, Dict, Any, AsyncGenerator
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from agents import Runner, function_tool, WebSearchTool, Agent
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
from openai import AsyncAzureOpenAI
from agents import set_default_openai_client
import time
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
from agents import OpenAIResponsesModel, AsyncOpenAI, OpenAIChatCompletionsModel
class StreamWithRetry:
    def __init__(self, runner_func, agent, input_text, max_retries=5, initial_delay=10, max_delay=60):
        self.runner_func = runner_func
        self.agent = agent
        self.input_text = input_text
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay

    async def _process_stream(self, result):
        """Process the entire stream and yield only text deltas."""
        try:
            async for event in result.stream_events():
                event_type = event.type
                event_data = getattr(event, 'data', None)
                if event_type == "raw_response_event" and isinstance(event_data, ResponseTextDeltaEvent):
                    yield event_data.delta
        except Exception as e:
            print(f"\nError during stream processing: {str(e)}")
            raise

    async def stream_events(self) -> AsyncGenerator[str, None]:
        """Get the stream events, ensuring we have a valid iterator first."""
        delay = self.initial_delay
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                # Get the iterator
                result = self.runner_func(self.agent, self.input_text)
                # Process the entire stream
                async for delta in self._process_stream(result):
                    yield delta
                # If we get here, the stream completed successfully
                print(f"Stream completed successfully")
                print(f"usage details: {result.context_wrapper.usage}")
                if attempt > 0:
                    print(f"\nRetry attempt {attempt + 1} successful")
                return
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries:
                    print(f"\nAttempt {attempt + 1} failed with error: {str(e)}")
                    if "Rate limit is exceeded" in str(e):
                        try:
                            wait_time = int(str(e).split("Try again in ")[1].split(" seconds")[0])
                            print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                            continue
                        except:
                            pass
                    print(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, self.max_delay)
                else:
                    print(f"\nAll {self.max_retries + 1} attempts failed")
                    raise last_exception

class ActivityStatus(str, Enum):
    COMPLETED = "Completed"
    PARTIALLY_COMPLETED = "Partially completed"
    NEEDS_USER_CONFIRMATION = "Needs user confirmation"

class ActivityImportance(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class HealthActivityRecommendation(BaseModel):
    recommendation: str = Field(..., description="The specific recommendation")
    importance: ActivityImportance = Field(..., description="Importance level of the activity")
    recommendation_reason: str = Field(..., description="What do you know about this patient's data that makes you belive this recommendation is relevant for this particulat patient.")
    benefit: str = Field(..., description="why is this important for their health and what are the benfits.")
    impact_of_not_doing: str = Field(..., description="what are the potential consequences of not doing this.")
    frequency: str = Field(..., description="how often should the patient be doing this activity")
    source: str = Field(..., description="what is the source of the recommendation")
    recommendation_short_str: str = Field(..., description="A short version of the recommendation string to display to the user on a mobile device.")
    frequency_short_str: str = Field(..., description="A very short version of the frequency string to display to the user on a mobile device.")

class HealthActivityRecommendationCategory(BaseModel):
    category_name: str = Field(..., description="Name of the health category")
    recommendations: List[HealthActivityRecommendation] = Field(..., description="List of health activity recommendations")

class HealthActivityRecommendationList(BaseModel):
    categories: List[HealthActivityRecommendationCategory] = Field(..., description="List of health activity recommendations")


class HealthActivityAssessmentOutput(BaseModel):
    status: ActivityStatus = Field(..., description="Current status of the activity")
    next_step_recommendation: Optional[str] = Field(None, description="If the activity was not completed, what is the next step recommendation")
    supporting_evidence: Optional[str] = Field(None, description="What evidence the patient's health data may have to support the assessment")
    user_input_questions: Optional[List[str]] = Field(None, description="List of yes/no questions that need to be asked to the user to confirm the activity status")


class HealthActivityAssessment(BaseModel):
    activity: HealthActivityRecommendation = Field(..., description="The recommended health activity")
    status: ActivityStatus = Field(..., description="Current status of the activity")
    next_step_recommendation: Optional[str] = Field(None, description="If the activity was not completed, what is the next step recommendation")
    supporting_evidence: Optional[str] = Field(None, description="What evidence the patient's health data may have to support the assessment")
    user_input_questions: Optional[List[str]] = Field(None, description="List of yes/no questions that need to be asked to the user to confirm the activity status")

class HealthCategory(BaseModel):
    category_name: str = Field(..., description="Name of the health category")
    activities: List[HealthActivityAssessment] = Field(..., description="List of health activities in this category")

class HealthAssessmentOutput(BaseModel):
    categories: List[HealthCategory] = Field(..., description="List of health categories with their activities")
    assessment_date: str = Field(..., description="Date and time when the assessment was performed")

class HealthCareAgent:
    def __init__(self):
        self.current_date_and_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.uspstf_data = self._load_uspstf_data()
        self.risk_inv_map = {v["code"]: k for k, v in self.uspstf_data["risks"].items()}
        self._initialize_agents()

    def _load_uspstf_data(self):
        with open("USPSTF_formatted_json.json", "r") as f:
            return json.load(f)

    async def _run_with_retry(self, runner_func, agent, input_text, max_retries=5, initial_delay=10, max_delay=60, is_streamed=False):
        """
        Run a Runner function with exponential backoff retry logic.
        
        Args:
            runner_func: The Runner function to call (Runner.run or Runner.run_streamed)
            agent: The agent to run
            input_text: The input text for the agent
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds before first retry
            max_delay: Maximum delay in seconds between retries
            is_streamed: Whether to use streaming mode
            
        Returns:
            The result from the runner function
        """
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                if is_streamed:
                    # For streaming, we need to handle the async generator differently
                    try:
                        result = runner_func(agent, input_text)
                        if attempt > 0:
                            print(f"\nRetry attempt {attempt + 1} successful")
                        return result
                    except Exception as e:
                        if "Rate limit is exceeded" in str(e):
                            # Extract the wait time from the error message if possible
                            try:
                                wait_time = int(str(e).split("Try again in ")[1].split(" seconds")[0])
                                print(f"\nRate limit exceeded. Waiting for {wait_time} seconds...")
                                await asyncio.sleep(wait_time)
                                continue
                            except:
                                # If we can't parse the wait time, use our exponential backoff
                                raise e
                        else:
                            raise e
                else:
                    result = await runner_func(agent, input_text, max_turns=5)
                    if attempt > 0:
                        print(f"\nRetry attempt {attempt + 1} successful")
                    return result
                    
            except Exception as e:
                last_exception = e
                if attempt < max_retries:
                    print(f"\nAttempt {attempt + 1} failed with error: {str(e)}")
                    if "Rate limit is exceeded" in str(e):
                        try:
                            wait_time = int(str(e).split("Try again in ")[1].split(" seconds")[0])
                            print(f"Rate limit exceeded. Waiting for {wait_time} seconds...")
                            await asyncio.sleep(wait_time)
                            continue
                        except:
                            pass
                    print(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, max_delay)  # Exponential backoff with max delay
                else:
                    print(f"\nAll {max_retries + 1} attempts failed")
                    raise last_exception

    def _query_uspstf_guidelines(
        self,
        age: Optional[int] = None,
        sex: Optional[str] = None,
        pregnant: Optional[str] = None,
        tobacco: Optional[str] = None,
        sexually_active: Optional[str] = None,
        bmi: Optional[str] = None
    ) -> str:
        """Query USPSTF guidelines based on patient characteristics."""
        print("Tool Call: Query USPSTF guidelines.")
        print(f"age: {age}, sex: {sex}, pregnant: {pregnant}, tobacco: {tobacco}, sexually_active: {sexually_active}, bmi: {bmi}")
        matching_recommendations = []
        
        for r in self.uspstf_data["specificRecommendations"]:
            if age is not None and not (r["ageRange"][0] <= age <= r["ageRange"][1]):
                continue
            if r["grade"] != "A" and r["grade"] != "B":
                continue
            if sex is not None and r["sex"] != "men and women" and r["sex"] != sex:
                continue
                
            risk_conditions_met = True
            if "risk" in r and r["risk"] is not None and len(r["risk"]) > 0:
                if pregnant == "Y" and not any(self.risk_inv_map.get(risk) == "PREGNANT" for risk in r["risk"]):
                    risk_conditions_met = False
                if tobacco == "Y" and not any(self.risk_inv_map.get(risk) == "TOBACCO" for risk in r["risk"]):
                    risk_conditions_met = False
                if sexually_active == "Y" and not any(self.risk_inv_map.get(risk) == "SEXUALLYACTIVE" for risk in r["risk"]):
                    risk_conditions_met = False
                    
            if not risk_conditions_met:
                continue
                
            if bmi is not None and "bmi" in r:
                if not (r["bmi"] == bmi or 
                       (bmi in ["O", "OB"] and r["bmi"] == "N") or 
                       (bmi == "OB" and r["bmi"] == "O")):
                    continue
                    
            recommendation = {
                "id": r["id"],
                "title": r["title"],
                "importance": "High" if r["grade"] == "A" else "Medium" if r["grade"] == "B" else "Low",
                "sex": r["sex"],
                "age_range": r["ageRange"],
                "text": r["text"],
                "rationale": r.get("rationale", ""),
                "service_frequency": r.get("servFreq", ""),
                "risk_text": r.get("riskText", ""),
                "bmi": r.get("bmi", ""),
                "grade_text": self.uspstf_data["grades"][r["grade"]][r["gradeVer"]],
                "source": "USPSTF"
            }
            matching_recommendations.append(recommendation)
        
        text_output = ""
        for r in matching_recommendations:
            text_output += f"""Action/Task: {r['title']}
                  Importance: {r['importance']}
                  Text: {r['text']}
                  Rationale: {r['rationale']}
                  Service Frequency: {r['service_frequency']}
                  Risk Text: {r['risk_text']}
                  Source: USPSTF \n\n"""
        #print(text_output)
        return text_output

    def _get_patient_info(self) -> str:
        """Get patient information."""
        print("Tool Call: Get Detailed Patient data.")
        patient_file_dir = "/Users/nitingoel/AI/experiments/Health Datasets/Synthea/synthea/output/text"
        #patient_file_name = "Blair400_Bernier607_1b89bede-f50a-fa66-1a2c-b126a249bc81.txt"
        patient_file_name = "Kassandra256_Francie486_Sawayn19_ad2aa304-bf4a-c2c5-a8ff-2c217f2ea1f5.txt"
        #patient_file_name = "nitin_goel.txt"
        patient_file_dir = "/Users/nitingoel/tmp"
        patient_file_name = "demo1.txt"

        patient_file_path = os.path.join(patient_file_dir, patient_file_name)
        with open(patient_file_path, "r") as f:
            patient_info = f.read()
        return patient_info
    
    async def _perform_web_research(self, query: str) -> str:
        """Perform a web search."""
        print("Tool Call: Perform a web search.")
        print(f"Query Provided to Web Research Tool: {query}")
        perplexity_client = AsyncOpenAI(base_url="https://api.perplexity.ai", api_key=os.getenv("PERPLEXITY_API_KEY"))
        perplexity_agent = Agent(
            name="Perplexity agent",
            instructions="You will leverage web search to identify latest health guidelines and recommendations for a given patient. The query provided to you will be the high level description of the patient. You will use this query to search the web for the latest health guidelines and recommendations for this patient. You will focus on guidelines and recommendations that are clear, specific and actionable by the patient. We are looking to assess which of these are being followed by the patient per recommended frequency. You will then enumerate each guideline and recommendation along with the reasoning why they should be following each recommendation and the frequency at which this particular recommendation may need to be followed by such a patient.",
            model=OpenAIChatCompletionsModel( 
                model="sonar-reasoning-pro",
                openai_client=perplexity_client,
            ),
        )
        response = await Runner.run(perplexity_agent, query)
        #print(f"Response from Perplexity Agent: {response.final_output}")
        return response.final_output


    def _initialize_agents(self):
        # Create the function tool wrapper
        self.query_uspstf_guidelines = function_tool(self._query_uspstf_guidelines)
        self.get_patient_info = function_tool(self._get_patient_info)
        self.perform_web_research = function_tool(self._perform_web_research)
        self.azure_client = AsyncAzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2025-04-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        #set_default_openai_client(self.azure_client) disable azure and use the normal client

        self.patient_data_basic_summary_agent = Agent(
            name="Health Care Patient Data Summarizer",
            instructions=f"""Provide a very biref summary of patient's health data in a sentence or two that includes the patient's age, sex, and any other basic demographic information. A different agent will use this to conduct a web search to identify general health guidelines and recommendations for such kinds of patients. Do not specific details about the patient's data outside of basic demographics, so the search focuses on the most basic general guidelines that generally apply to patients like this, without being influenced by the specific conditions or risk factors that may be unique to them.
            
            """,
            model="gpt-4o-mini",
            tools=[self.get_patient_info],
        )

        self.patient_data_advanced_summary_agent = Agent(
            name="Health Care Patient Data Advanced Summarizer",
            instructions=f"""Provide a short description of this patient's health data in a few senteces that includes basic demographics and any pertinent information about the patient's health data which would influence the kind of health guidelines and recommendations that would be uniquely applicable to them based on their health data.

            A different agent will use this summary to conduct a web search to identify general health guidelines and recommendations for patients with the sepecific situations you outline. Do not make any recommendations of your own, just provide clear facts that are mentioned in the health record. Let the other agent make the assessment on recommendations based on their knowledge and internet searches.
            
            """,
            model="gpt-4o-mini",
            tools=[self.get_patient_info],
        )

        self.activity_recommender_agent = Agent(
            name="Health Care Activity Recommender",
            output_type=HealthActivityRecommendationList,
            instructions=f"""You will be given high level information about a patietnt. Your goal is to use the perform_web_research tool to research known health guidelines to generate a list of activities, by category, of things the patient should be doing for their health. These activities could include but are not limited to health screenings, vaccinations, following any dietary recommendations or exercise recommendations and more.

            You will use what you have been told about the patient and use internet search using the perform_web_research tool to identify what are the latest guidelines and recommendations for such patients.

            Web searches are expensive and time consuming, so make sure to use the perform_web_research tool wisely. Conduct no more than 4 web searches.
            
            Your final output should be a list of recommended actions/tasks grouped by category. For each recommended action/task, specify:
            1. Recommendation: The specific recommendation.
            2. Level of importance: how important is this to their health.
            3. Frequency: how frequently should be doing it. Do not be vague on the frequency, specify it in a measurable way so that a separate agent can review the detailed medical record to assess whether that activity was completed within that recent timeframe. If a certain activity is only as needed and left at the patient's discretion, then say that and do not try to impose a frequency on it. 
            4. Reason for recommendation: What do you know about this patient's data that makes you belive this recommendation is relevant for this particulat patient.
            5. Benefit of following this recommendation: why is this important for their health and what are the benfits.
            6. Impact of not doing this: what are the potential consequences of not doing this.
            7. Source: what is the source of the recommendation.

            Your inputs will be used by another agent to assess whether the patient has completed the activity/task within the prescribed timeframe.

            The current date and time is: {self.current_date_and_time}
            """,
            model="gpt-4o-mini",
            tools=[self.perform_web_research],
        )

        self.uspstf_guideline_recommender_agent = Agent(
            name="USPSTF Guideline Recommender",
            output_type=HealthActivityRecommendationList,
            instructions=f"""You are an agent that specializes in analyzing USPSTF guidelines and matching them to patient data. Your goal is to:

            1. Use the query_uspstf_guidelines tool to get relevant USPSTF recommendations based on the patient's characteristics
            2. Review the patient's health data to determine which recommendations are truly applicable
            3. Convert the applicable recommendations into a structured list of health activities

            When using the query_uspstf_guidelines tool, you must provide the following parameters:
            - age: The patient's age in years (integer)
            - sex: Either "male" or "female" (string)
            - pregnant: "Y" if pregnant, "N" if not pregnant, or None if unknown (string)
            - tobacco: "Y" if tobacco user, "N" if not, or None if unknown (string)
            - sexually_active: "Y" if sexually active, "N" if not, or None if unknown (string)
            - bmi: "N" for normal, "O" for overweight, "OB" for obese, or None if unknown (string)

            For each recommendation from USPSTF that you determine is applicable to the patient, you should:
            1. Extract the specific recommendation and convert it into a clear, actionable activity
            2. Set the importance level based on the USPSTF grade (A = High, B = Medium)
            3. Extract or infer the frequency from the recommendation text
            4. Explain why this recommendation is relevant for this specific patient based on their health data
            5. Include the benefits and potential consequences from the USPSTF recommendation
            6. Clearly indicate that the source is USPSTF

            Your output should follow the HealthActivityRecommendationList format, with each recommendation containing:
            1. Recommendation: The specific recommendation.
            2. Level of importance: how important is this to their health.
            3. Frequency: how frequently should be doing it. Do not be vague on the frequency, specify it in a measurable way so that a separate agent can review the detailed medical record to assess whether that activity was completed within that recent timeframe. If a certain activity is only as needed and left at the patient's discretion, then say that and do not try to impose a frequency on it. 
            4. Reason for recommendation: What do you know about this patient's data that makes you belive this recommendation is relevant for this particulat patient.
            5. Benefit of following this recommendation: why is this important for their health and what are the benfits.
            6. Impact of not doing this: what are the potential consequences of not doing this.
            7. Source: what is the source of the recommendation.

            Only include recommendations that are truly applicable to the patient based on their health data.
            The current date and time is: {self.current_date_and_time}
            """,
            model="gpt-4o",
            tools=[self.get_patient_info, self.query_uspstf_guidelines],
        )

        self.activity_list_consolidator_agent = Agent(
            name="Health Care Activity List Consolidator",
            output_type=HealthActivityRecommendationList,
            instructions=f"""You are an agent that will review different health activity recommendations made by other agents for a given patient, and review them agaisnt the patient's health data and your own knowledge and common sense. 
            
            You will be given a list of health activity recommendations made by other agents for a given patient in JSON format. Since different agents may have made recommendations for the same activity or similar acttivities in different ways, you will need to consolidate them into a single list of activities/tasks by category. 

            Each activity should be unique and not redundant. Each activity should be specific, actionable and achievableby the patient and have a meaningful impact on their health. Do not include activities that are vague and hard to assess for completion. Also do not try and combine too many activities or recommendations into a single activity. Doing so makes it very hard to assess it for completion. Break them down into individual activity recommendations, or group together things that are typically always done together, so we can mark that group as completed. Feel free to re-think the categories and organize the unique activities into the most relevant categories. At a minimum, we should have a one category for Health screenings. We could have one cateogry for vaccinations if any vaccination related activities were recommended and deemed relevant. For the remaining activities, feel free to group them using the most appropriate category names. 
            
            The category name should not exceed 28 characters. Ensure there are no more than 4 categories and no more than 5 activities per category. Fewer are okay. So pick the most relevant ones.

            Discard any recommendations that are not applicable to the patient. 

            Your final output should be a smaller consolidated and a much more focused list of recommended actions/tasks grouped by category. For each recommended action/task, specify:
            1. Recommendation: The specific recommendation.
            2. Level of importance: how important is this to their health.
            3. Frequency: how frequently should be doing it. Do not be vague on the frequency, specify it in a measurable way so that a separate agent can review the detailed medical record to assess whether that activity was completed within that recent timeframe. If a certain activity is only as needed and left at the patient's discretion, then say that and do not try to impose a frequency on it. 
            4. Reason for recommendation: What do you know about this patient's data that makes you belive this recommendation is relevant for this particulat patient.
            5. Benefit of following this recommendation: why is this important for their health and what are the benfits.
            6. Impact of not doing this: what are the potential consequences of not doing this.
            7. Source: what is the source of the recommendation.

            In addition, because the recommendation and its frequency will be displayed on a mobile device, you should also provide a short version of the recommendation and frequency. We will display the short version of the recommendation as a title and the short version of the frequency as a subtitle. Do not duplicate information between the two, specifically the recommendation short string should not also have any information about the frequency at which it should be done because in the UI it will show duplicated in the frequency short string.

            8. Recommendation short string: A short version of the recommendation string to display to the user on a mobile device (line 1). Not to exceed 35 characters. Do not include any information about the frequency here.
            9. Frequency short string: A very short version of the frequency string to display to the user on a mobile device (line 2).  Not to exceed 35 characters.

            """,
            model="o3-mini",
            tools=[self.get_patient_info],
        )

        self.activity_assessment_agent = Agent(
            name="Health Care Activity Assessment Agent",
            output_type=HealthActivityAssessmentOutput,
            instructions=f"""Your goal is to assess whether a patient's health data indicates that they have completed the health related task or activitiy within the prescribed timeframe.

            As an input to you, you will be given details of a single recommendation made by an AI agent for this patient. 
            You will also be given the patient's health data. Here's a hint, sometimes the encounter data does not have details of what was done in that encounter. A hint is to look at observations done around the same time. That might give you more information of what was done.

            You will then access the patient's health data to assess whether:
            a) The health data you have includes information which may help you assess whether they have fully or partially done this activity or followed that recommendation within the prescribed timeframe.
            b) If yes, then you should capture the evidence that supports the assessment.
            c) If the patient's data does not have information which would allow the assessment to complete, and needs more inputs from the user, you should indicate that and recommend what question to ask the user. The questions must be simple yes/no questions and not open ended questions. You can choose to ask more than one question if needed.
            
            Your output should be a JSON object that matches the HealthActivityAssessmentOutput Pydantic model.
                status: One of the following: Completed, Partially completed, Needs user confirmation.
                next_step_recommendation: If the activity was not completed or partially completed, what is the next step recommendation
                supporting_evidence: What evidence the patient's health data may have to support the assessment
                user_input_questions: List of yes/no questions that need to be asked to the user to confirm the activity status. It is important that the questions are framed in a way that the user can simply respond with a yes or no. A yes to all questions should be interpreted as the activity being completed.

            The current date and time is: {self.current_date_and_time}
            """,
            model="o3-mini",
        )

    async def review_patient(self):
        """Run the patient review process."""
        try:

            print("Running patient data basic summary agent")
            #set_default_openai_client(self.azure_client) commenting out to use default openai client
            
            # Use StreamWithRetry for streaming responses
            streamer = StreamWithRetry(
                Runner.run_streamed,
                self.patient_data_basic_summary_agent,
                "fetch patient data and generate summary."
            )
            basic_summary = ""
            async for delta in streamer.stream_events():
                basic_summary += delta
                print(delta, end="", flush=True)
            print(f"\n\n")

            print("Running patient data advanced summary agent")
            streamer = StreamWithRetry(
                Runner.run_streamed,
                self.patient_data_advanced_summary_agent,
                "fetch patient data and generate summary."
            )
            advanced_summary = ""
            async for delta in streamer.stream_events():
                advanced_summary += delta
                print(delta, end="", flush=True)
            print(f"\n\n")

            print(f"Running health activity recommender agent using: {basic_summary}")
            result = await self._run_with_retry(Runner.run, self.activity_recommender_agent, basic_summary)
            basic_recommendations = result.final_output_as(HealthActivityRecommendationList)
            #print usage details
            print(f"Usage details: {result.context_wrapper.usage}")
            total_recommendations = sum(len(category.recommendations) for category in basic_recommendations.categories)
            print(f"\n\nFound {len(basic_recommendations.categories)} categories with {total_recommendations} recommendations using basic summary\n\n")

            print(f"Running health activity recommender agent using summary: {advanced_summary}")
            result = await self._run_with_retry(Runner.run, self.activity_recommender_agent, advanced_summary)
            advanced_recommendations = result.final_output_as(HealthActivityRecommendationList)
            total_recommendations = sum(len(category.recommendations) for category in advanced_recommendations.categories)
            print(f"\n\nFound {len(advanced_recommendations.categories)} categories with {total_recommendations} recommendations using advanced summary\n\n")

            print("Running health activity recommender agent using USPSTF  guidelines")
            result = await self._run_with_retry(Runner.run, self.uspstf_guideline_recommender_agent, "Generate a list of health activities/tasks that the patient should be doing based on their health data.")
            uspstf_recommendations = result.final_output_as(HealthActivityRecommendationList)
            total_recommendations = sum(len(category.recommendations) for category in uspstf_recommendations.categories)
            print(f"\n\nFound {len(uspstf_recommendations.categories)} categories with {total_recommendations} recommendations using USPSTF guidelines\n\n")

            # Combine all categories into a new HealthActivityRecommendationList
            combined_recommendations = HealthActivityRecommendationList(
                categories=basic_recommendations.categories + advanced_recommendations.categories + uspstf_recommendations.categories
            )
            total_recommendations = sum(len(category.recommendations) for category in combined_recommendations.categories)    

            #share all the combined recommendations to the activity_list_consolidator_agent agent to consolidate them into a smaller list
            result = await self._run_with_retry(Runner.run, self.activity_list_consolidator_agent, combined_recommendations.model_dump_json(indent=4))
            consolidated_recommendations = result.final_output_as(HealthActivityRecommendationList)
            total_recommendations = sum(len(category.recommendations) for category in consolidated_recommendations.categories)
            print(f"\n\nConsolidated recommendations down to a smaller list of {len(consolidated_recommendations.categories)} categories with {total_recommendations} recommendations\n\n")

            # Process each recommendation through the activity assessment agent
            final_categories = []
            # Get patient data
            patient_data = self._get_patient_info()
            for category in consolidated_recommendations.categories:
                assessed_activities = []
                for recommendation in category.recommendations:
                    
                    # Create input combining recommendation and patient data
                    assessment_input = {
                        "recommendation": recommendation.model_dump(),
                        "patient_data": patient_data
                    }
                    
                    # Pass both recommendation and patient data to the activity assessment agent
                    print(f"Running activity assessment agent for recommendation: {recommendation.recommendation}")
                    result = await self._run_with_retry(Runner.run, self.activity_assessment_agent, json.dumps(assessment_input, indent=4))
                    assessment = result.final_output_as(HealthActivityAssessmentOutput)
                    
                    # Create a HealthActivityAssessment combining the recommendation and assessment
                    activity_assessment = HealthActivityAssessment(
                        activity=recommendation,
                        status=assessment.status,
                        next_step_recommendation=assessment.next_step_recommendation,
                        supporting_evidence=assessment.supporting_evidence,
                        user_input_questions=assessment.user_input_questions
                    )
                    assessed_activities.append(activity_assessment)
                
                # Create a new category with the assessed activities
                final_category = HealthCategory(
                    category_name=category.category_name,
                    activities=assessed_activities
                )
                final_categories.append(final_category)

            # Construct the final HealthAssessmentOutput
            final_output = HealthAssessmentOutput(
                categories=final_categories,
                assessment_date=self.current_date_and_time
            )
            #print json of final output
            print(f"\n\nFinal output: {final_output.model_dump_json(indent=4)}\n\n")

            #write the final output to a file
            with open("final_output.json", "w") as f:
                f.write(final_output.model_dump_json(indent=4))
                    
            return {
                "final_output": final_output.model_dump_json(indent=4),
                "message_history": result.to_input_list()
            }
        except Exception as e:
            import traceback
            print("\nError occurred in review_patient:")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print("\nFull traceback:")
            print(traceback.format_exc())
            raise  # Re-raise the exception after printing details

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

healthcare_agent = None

@app.on_event("startup")
async def startup_event():
    global healthcare_agent
    # Apply nest_asyncio here instead
    nest_asyncio.apply()
    
    # Initialize the healthcare agent
    healthcare_agent = HealthCareAgent()

@app.get("/")
def read_root():
    return {"hello": "world"}

@app.get("/ping")
def ping():
    return {"ping": "pong"}

@app.post("/review-patient")
async def review_patient():
    """Endpoint to trigger patient review."""
    if healthcare_agent is None:
        return {"error": "Healthcare agent not initialized"}
    return await healthcare_agent.review_patient()

# add another API to read the final_output.json file and return it as a response
@app.get("/get-final-output")
def get_final_output():
    with open("final_output.json", "r") as f:
        return json.load(f)

@app.get("/get-recommendations-summary", response_class=Response)
def get_recommendations_summary():
    """Endpoint to get a plain text summary of recommendations."""
    try:
        with open("final_output.json", "r") as f:
            data = json.load(f)
        
        summary = []
        summary.append("Health Recommendations Summary\n")
        summary.append("=" * 50 + "\n")
        
        for category in data["categories"]:
            summary.append(f"\n{category['category_name']}")
            summary.append("-" * len(category['category_name']))
            
            for activity in category["activities"]:
                recommendation = activity["activity"]["recommendation_short_str"]
                frequency = activity["activity"]["frequency_short_str"]
                status = activity["status"]
                
                summary.append(f"\n• {recommendation}")
                summary.append(f"  Frequency: {frequency}")
                summary.append(f"  Status: {status}")
                
                # Add questions if they exist and status needs confirmation
                if status == "Needs user confirmation" and activity.get("user_input_questions"):
                    summary.append("  Questions to confirm:")
                    for question in activity["user_input_questions"]:
                        summary.append(f"    - {question}")
            
            summary.append("\n")
        
        return Response(content="\n".join(summary), media_type="text/plain")
    except Exception as e:
        return Response(content=f"Error generating summary: {str(e)}", status_code=500, media_type="text/plain")
