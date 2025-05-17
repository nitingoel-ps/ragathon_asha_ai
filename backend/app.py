import os
import nest_asyncio
import json
from typing import Optional, List, Dict, Any
from fastapi import FastAPI
from agents import Runner, function_tool, WebSearchTool, Agent
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class ActivityStatus(str, Enum):
    COMPLETED = "Completed"
    NEVER_DONE = "Never done"
    OVERDUE = "Overdue"
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
        patient_file_name = "Blair400_Bernier607_1b89bede-f50a-fa66-1a2c-b126a249bc81.txt"
        patient_file_path = os.path.join(patient_file_dir, patient_file_name)
        with open(patient_file_path, "r") as f:
            patient_info = f.read()
        return patient_info
    
    def _initialize_agents(self):
        # Create the function tool wrapper
        self.query_uspstf_guidelines = function_tool(self._query_uspstf_guidelines)
        self.get_patient_info = function_tool(self._get_patient_info)

        self.patient_data_basic_summary_agent = Agent(
            name="Health Care Patient Data Summarizer",
            instructions=f"""Provide a very biref summary of patient's health data in a sentence or two that includes the patient's age, sex, and any other basic demographic information. A different agent will use this to conduct a web search to identify general health guidelines and recommendations for such kinds of patients. Do not specific details about the patient's data outside of basic demographics, so the search focuses on the most basic general guidelines that generally apply to patients like this, without being influenced by the specific conditions or risk factors that may be unique to them.
            
            """,
            model="gpt-4o",
            tools=[self.get_patient_info],
        )

        self.patient_data_advanced_summary_agent = Agent(
            name="Health Care Patient Data Advanced Summarizer",
            instructions=f"""Provide a short description of this patient's health data in a few senteces that includes basic demographics and any pertinent information about the patient's health data which would influence the kind of health guidelines and recommendations that would be uniquely applicable to them based on their health data.

            A different agent will use this summary to conduct a web search to identify general health guidelines and recommendations for patients with the sepecific situations you outline. Do not make any recommendations of your own, just provide clear facts that are mentioned in the health record. Let the other agent make the assessment on recommendations based on their knowledge and internet searches.
            
            """,
            model="gpt-4o",
            tools=[self.get_patient_info],
        )

        self.activity_recommender_agent = Agent(
            name="Health Care Activity Recommender",
            output_type=HealthActivityRecommendationList,
            instructions=f"""You will be given high level information about a patietnt. Your goal is to research known health guidelines to generate a list of activities, by category, of things they should be doing. These activities could include but are not limited to health screenings, vaccinations, completing follow up activities that their provider recommended, following any dietary recommendations or exercise recommendations and more.

            You will use what you have been told about the patient and use internet search to identify what are the latest guidelines and recommendations for such patients.
            
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
            model="gpt-4.1",
            tools=[WebSearchTool()],
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

            Each activity should be unique and not redundant. Each activity should be specific, actionable and achievableby the patient and have a meaningful impact on their health. Do not include activities that are vague and hard to assess for completion. Also do not try and combine too many activities or recommendations into a single activity. Doing so makes it very hard to assess it for completion. Break them down into individual activity recommendations, or group together things that are typically always done together, so we can mark that group as completed.
            

            Discard any recommendations that are not applicable to the patient. 

            Your final output should be a smaller consolidated and a much more focused list of recommended actions/tasks grouped by category. For each recommended action/task, specify:
            1. Recommendation: The specific recommendation.
            2. Level of importance: how important is this to their health.
            3. Frequency: how frequently should be doing it. Do not be vague on the frequency, specify it in a measurable way so that a separate agent can review the detailed medical record to assess whether that activity was completed within that recent timeframe. If a certain activity is only as needed and left at the patient's discretion, then say that and do not try to impose a frequency on it. 
            4. Reason for recommendation: What do you know about this patient's data that makes you belive this recommendation is relevant for this particulat patient.
            5. Benefit of following this recommendation: why is this important for their health and what are the benfits.
            6. Impact of not doing this: what are the potential consequences of not doing this.
            7. Source: what is the source of the recommendation.

            In addition, because the recommendation and its frequency will be displayed on a mobile device, you should also provide a short version of the recommendation and frequency. We will display the short version of the recommendation as a title and the short version of the frequency as a subtitle. Do not duplicate information between the two.

            8. Recommendation short summary: A short version of the recommendation string to display to the user on a mobile device (line 1).
            9. Frequency short summary: A very short version of the frequency string to display to the user on a mobile device (line 2).

            Ensure there are no more than 3 categories and no more than 5 activities per category. Fewer are okay. So pick the most relevant ones.
            """,
            model="o3-mini",
            tools=[self.get_patient_info],
        )

        self.activity_assessment_agent = Agent(
            name="Health Care Activity Assessment Agent",
            output_type=HealthActivityAssessmentOutput,
            instructions=f"""Your goal is to assess whether a patient's health data indicates that they have completed the health related task or activitiy within the prescribed timeframe.

            As an input to you, you will be given details of a single recommendation made by an AI agent for this patient. 
            You will also be given the patient's health data.

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

        self.orchestrator_agent = Agent(
            name="Health Care Assessment Orchestrator",
            output_type=HealthAssessmentOutput,
            instructions=f"""You are an orchestrator, that will use the available tools to assess the provided patient data. 

            Your goal is to assess what health related actions the patient should be taking, compare them to what the patient has done vs is not indicated as done based on the patient data.

            You will first use the activity recommender agent to generate a list of recommended activities/tasks by category that the paretient should be doing based on their health data. This tool does not have access to any information about the patient, it only uses the information provided to it by you in plain language. You should use this tool to generate the list of recommended activities/tasks. You should plan to use this tool exactly twice. Once using only the patient's age, sex and basic demographics. Then a second time using the patient's age, sex, basic demographics and the specific conditions and risk factors. 

            Next you will use the uspstf_guideline_recommender agent to get recommendations directly from the USPSTF guidelines database. This agent will analyze the patient's data and match it against USPSTF guidelines to generate a list of applicable recommendations.

            You would then use the activity_list_consolidator tool to consolidate all the lists of recommendations you got from the activity_recommender tool and the uspstf_guideline_recommender tool, into a smaller focused list of recommended activities/tasks. You would need to pass it all the outputs you have received from all the different calls you made to the activity_recommender tool and the uspstf_guideline_recommender tool.

            Once you have the focused consolidated list of recommened activities/tasks, you must then call the activity assessment agent for each activity/task.  This tool will perform a detailed assessment of whether the patient data indicates that the patient has completed the activity/task within the prescribed timeframe. It will then provide you with its findings, including what evidence the patient's health data may have to support the assessment.
             
               It is important to pass the relevant context to the activity assessment agent so that it can make the best assessment. Please include the following context in the input to the activity assessment agent for each activity/task. Send this data in key value pairs.
            1. The activity Cateogry
            2. The name of the activity
            3. Recommended frequency
            4. Rationale for why it may be needed.

            Once you have all the information, you will then produce a final output back to the user.
             The output shoudld contain the following elements represented in the HealthAssessmentOutput Pydantic model.

            1. A list of categories, each containing:
               - A category name
               - A list of health activities, each containing:
                 - Action name
                 - Status (one of: Completed, Never done, Overdue, Needs user confirmation)
                 - Importance (one of: High, Medium, Low)
                 - Rationale (why this is important for their health and what are the benefits)
                 - Impact of not doing this (what are the consequences)
                 - Frequency (how often should the patient be doing this)
                 - Next step recommendation (if the activity was not completed)
                 - Supporting evidence (what evidence the patient's health data may have to support the assessment)
                 - List of questions to ask the user to confirm the activity status (if status is Needs user confirmation)

            The current date and time is: {self.current_date_and_time}
            """,
            model="gpt-4o-mini",
            tools=[
                self.get_patient_info,
                self.activity_recommender_agent.as_tool(
                    tool_name="activity_recommender",
                    tool_description="You can use this tool to generate a list of recommended activities/tasks by category that the paretient should be doing based on their health data. This tool does not have access to any information about the patient, it only uses the information you provide to it about the patient. It works best with plain language input mentioning the criteria for the person it should get recommendations for. It would them use its knowledge and internet searches to identify the latest recommendations of tasks/activities by category. The output would include the level of importance, frequency, rationale for doing this, and the impact of not doing this.",
                ),
                self.uspstf_guideline_recommender_agent.as_tool(
                    tool_name="uspstf_guideline_recommender",
                    tool_description="This tool analyzes USPSTF guidelines and matches them to patient data to generate a list of applicable recommendations. It uses the patient's health data to determine which USPSTF recommendations are truly relevant and converts them into actionable activities with importance levels, frequencies, and rationales.",
                ),
                self.activity_assessment_agent.as_tool(
                    tool_name="activity_assessment",
                    tool_description="""This tool assess whether a patient has completed a health related task or activitiy within the prescribed timeframe. You should pass it the following inputs as key value pairs:
                    1. The activity Cateogry
                    2. The name of the activity
                    3. Recommended frequency
                    4. Rationale for why it may be needed.
                    The tool's output would indicate whether the activity was done, when was it last done. If it was done within the prescribed timeframe. If the patient's data does not have information which would allow the assessment to complete, and needs confirmation from the user, it would return a message to the user to confirm the same. The assessment tool could also assess that this activity is not applicable or important for this specific patient and return that information."""
                ),
                self.activity_list_consolidator_agent.as_tool(
                    tool_name="activity_list_consolidator",
                    tool_description="""This agent will consolidate all the recommended health activities generated by the activity_recommender tools into a single conslidated and focused list. You should pass it all the outputs you have received from all the different calls you made to the activity_recommender tool.
                    """
                ),
            ]
        )

    async def review_patient(self):
        """Run the patient review process."""
        print("Running patient data basic summary agent")
        result = await Runner.run(self.patient_data_basic_summary_agent, "fetch patient data and generate summary.", max_turns=5)
        basic_summary = result.final_output
        print(f"\n\nBasic summary: {basic_summary}\n\n")

        print("Running patient data advanced summary agent")
        result = await Runner.run(self.patient_data_advanced_summary_agent, "fetch patient data and generate summary.", max_turns=5)
        advanced_summary = result.final_output  
        print(f"\n\nAdvanced summary: {advanced_summary}\n\n")


        print("Running health activity recommender agent using basic summary")
        result = await Runner.run(self.activity_recommender_agent, basic_summary, max_turns=5)
        basic_recommendations = result.final_output_as(HealthActivityRecommendationList)
        total_recommendations = sum(len(category.recommendations) for category in basic_recommendations.categories)
        print(f"\n\nFound {len(basic_recommendations.categories)} categories with {total_recommendations} total health activity recommendations using basic summary: {basic_recommendations.model_dump_json(indent=4)}\n\n")

        print("Running health activity recommender agent using advanced summary")
        result = await Runner.run(self.activity_recommender_agent, advanced_summary, max_turns=5)
        advanced_recommendations = result.final_output_as(HealthActivityRecommendationList)
        total_recommendations = sum(len(category.recommendations) for category in advanced_recommendations.categories)
        print(f"\n\nFound {len(advanced_recommendations.categories)} categories with {total_recommendations} total health activity recommendations using advanced summary: {advanced_recommendations.model_dump_json(indent=4)}\n\n")


        print("Running health activity recommender agent using USPSTF  guidelines")
        result = await Runner.run(self.uspstf_guideline_recommender_agent, "Generate a list of health activities/tasks that the patient should be doing based on their health data.", max_turns=5)
        uspstf_recommendations = result.final_output_as(HealthActivityRecommendationList)
        total_recommendations = sum(len(category.recommendations) for category in uspstf_recommendations.categories)
        print(f"\n\nFound {len(uspstf_recommendations.categories)} categories with {total_recommendations} total health activity recommendations using USPSTF guidelines: {uspstf_recommendations.model_dump_json(indent=4)}\n\n")

        # Combine all categories into a new HealthActivityRecommendationList
        combined_recommendations = HealthActivityRecommendationList(
            categories=basic_recommendations.categories + advanced_recommendations.categories + uspstf_recommendations.categories
        )
        total_recommendations = sum(len(category.recommendations) for category in combined_recommendations.categories)
        print(f"\n\nTotally now have {len(combined_recommendations.categories)} categories with {total_recommendations} total health activity recommendations: {combined_recommendations.model_dump_json(indent=4)}\n\n")
    
    
        #share all the combined recommendations to the activity_list_consolidator_agent agent to consolidate them into a smaller list
        result = await Runner.run(self.activity_list_consolidator_agent, combined_recommendations.model_dump_json(indent=4), max_turns=5)
        consolidated_recommendations = result.final_output_as(HealthActivityRecommendationList)
        total_recommendations = sum(len(category.recommendations) for category in consolidated_recommendations.categories)
        print(f"\n\nConsolidated recommendations down to a smaller list of {len(consolidated_recommendations.categories)} categories with {total_recommendations} total health activity recommendations: {consolidated_recommendations.model_dump_json(indent=4)}\n\n")

        # Process each recommendation through the activity assessment agent
        final_categories = []
        for category in consolidated_recommendations.categories:
            assessed_activities = []
            for recommendation in category.recommendations:
                # Get patient data
                patient_data = self._get_patient_info()
                
                # Create input combining recommendation and patient data
                assessment_input = {
                    "recommendation": recommendation.model_dump(),
                    "patient_data": patient_data
                }
                
                # Pass both recommendation and patient data to the activity assessment agent
                result = await Runner.run(
                    self.activity_assessment_agent,
                    json.dumps(assessment_input, indent=4),
                    max_turns=5
                )
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

        return {
            "final_output": final_output.model_dump_json(indent=4),
            "message_history": result.to_input_list()
        }

# Initialize FastAPI app
app = FastAPI()
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

