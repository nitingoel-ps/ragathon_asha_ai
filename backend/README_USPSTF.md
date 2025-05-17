# Prevention TaskForce API
## About Prevention TaskForce
The Prevention TaskForce is an application designed to help primary care clinicians identify the screening, counseling, and preventive medication
services that are appropriate for their patients. The Prevention TaskForce is available both as a web application, and as a mobile application.
The Prevention TaskForce information is based on the current recommendations of the U.S. Preventive Services Task Force (USPSTF) and can
be searched by keywords and specific patient characteristics, such as age, sex, and selected behavioral risk factors. The Prevention TaskForce
Web application can be accessed at https://www.uspreventiveservicestaskforce.org/. For more information on additional Prevention TaskForce
products, visit https://www.uspreventiveservicestaskforce.org/.

## Prevention TaskForce API Implementation
The Prevention TaskForce API is a web service that returns a filtered USPSTF recommendations data set according to the keywords and specific
patient characteristics, such as age, sex, selected behavioral risk factors, and recommendation grades as described in the Prevention TaskForce
API Data Usage and Format section using JSON. The following instructions provide field descriptions, object format, and sample code/queries
to implement and request JSON formatted Prevention TaskForce content. Access to Recommendations data API requires the use of an
authorized token key. We recommend downloading and caching the entire JSON data set locally for better data performance. JSON API can be
refreshed about once a week. In addition, the REST API support Last-Modified and ETag to determine topic data updates.
## Key Request
To request a key, please contact: uspstfpda@ahrq.gov
* Email subject: Requesting a Prevention TaskForce API key
* Email body:
    > Organization Name: ABC Company
    > Point of Contact: John Smith
    > Website URL: https://www.yourwebsiteurl.com

## Filtering Prevention TaskForce Data
The recommended use of the API is with local filtering.  An example filter for a specificRecommendation "r" follows.  It does not do keyword/text search, since one might want to strip the text before doing a search like that, but that is a trivial addition.
It assumes a few inputs such as:
* age param that is 0-99 or -1 if undefined
* sex param that is in the set of ["female","male","men and women"] or undefined
* pregnant as a boolean (set to false if not female or not pregnant, true if unknown)
* tobacco as a boolean (set to true if unknown)
* sexActive as a boolean (set to true if unknown)
* grades list that is empty if no grade filtering was selected
* bmi string that is one of the BMI values or undefined

Also, for snippet convenience, an inverted risk map for human readable lookup values.  That is, Object.entries(json.risks).map((a) => rInv.set(a[1].code,a[0]));
```
        if ( (age<0 || ( r.ageRange[0] <= age && age <= r.ageRange[1] )) &&
             (r.sex == "men and women" || !sex || sex == r.sex) &&
             (
                 (r.risk.includes(rInv.get("PREGNANT")) && pregnant) ||
                 (r.risk.includes(rInv.get("TOBACCO")) && tobacco)  ||
                 (r.risk.includes(rInv.get("SEXUALLYACTIVE")) && sexActive) ||
                 (!r.risk.includes(rInv.get("SEXUALLYACTIVE")) && !r.risk.includes(rInv.get("TOBACCO")) && !r.risk.includes(rInv.get("PREGNANT")))
             ) &&
             (!grades.length || grades.includes(r.grade)) &&
             (!bmi || r.bmi==bmi || ((bmi=="O" || bmi=="OB") && r.bmi=="N") || (bmi=="OB" && r.bmi=="O") ) )
            { console.log("include this recommendation") }
```
             
The following is a sample query string to send to the Prevention TaskForce API server containing all the parameters.  This querying is deprecated.
Server side filtering is discouraged and deprecated since the dataset rarely changes and is relatively small.
Client side filtering is the recommended approach now.  Nonetheless, the following query still functions for now.
?age=36&sex=female&pregnant=Y&tobacco=N&sexuallyActive=N&grade=A&grade=B&grade=C&grade=D&grade=I&tools=N&bmi=O
* age: integer between 0 to 99
* sex: male, female
* pregnant: Y, N   (requires sex of female) 
* tobacco: Y, N 
* sexuallyActive: Y, N
* grade: A, B, C, D, I (multiple values)
* tools: Y, N (returns only tools if Y)
* bmi: UW, N, O, OB

Omitting a search parameter typically means return all results for that category.
For example, if age is omitted, all ages are included, or if grade is omitted, all grades are included.

The following are more search query string examples:
?age=15
?age=36&sex=female&pregnant=Y
?tobacco=N
?tobacco=N&grade=A&grade=B

Additionally, a set of recommended online resources may be fetched by setting:
?tools=y
This action overrides all other parameters.  The Tools response is detailed at the end of the document.
The following is a basic format of the search response object. See the USPSTF Data Structure section for a more complete sample object:
specificRecommendations: [ {"key": "string/integer" .. } ],
grades: { "key": ["string","string"] .. },
generalRecommendations: { "key": { "key": "string/ integer array" ..} .. },
tools: { "key": { "key": "string" .. },
categories: {"key": {"key": "string"} },
risks: {"key": "string" }

## Specific Recommendations
The specificRecommendations array is sorted in the same order as the standard Prevention TaskForce Web search. 
Each object in the array represents a single specific recommendation aimed at a target population.
The following are specificRecommendations fields:
* id: integer identifying this specific recommendation
* title: title string
* grade: grade string the recommendation was given. Indexes into the grades object. see grades
* gradeVer: the integer version of the grade. index into the grade array. see grades
* gender: (deprecated) The sex of the target population.  This value is deprecated in favor of "sex" as the biological term.
* sex: The sex string of the target population. "female", "male", "men and women"
* ageRange: The ages the recommendation applies to. A two element integer array with a min of 0 and a max of 99.
* text: HTML format - text of the recommendation
* rationale: (optional) HTML format - rationale text for this recommendation. A fallback if a general rationale is not provided.
* servFreq (optional) HTML format - frequency of service text
* riskName (optional, deprecated) risk factor name string.  This value is maintained for legacy purposes, but further risks may be included in the risk array.
* risk (optional) Array of numbers identifying risks associated with this specific recommendation. See Risks
* riskText (optional) HTML format - risk factor comments
* general: string to index into the generalRecommendations object. see generalRecommendations
* tool: (deprecated) Array of tool id strings to index into tools associated with this specific recommendation. Tools at the specific recommendation level is deprecated. See Tools
* bmi: (optional) Weight category string based on BMI
    * "UW": Underweight - BMI is less than 18.5.
    * "N": Normal weight - BMI is 18.5 to 24.9.
    * "O": Overweight - BMI is 25 to 29.9.
    * "OB": Obese - BMI is 30 or more.

## Grades
The grades object consists of letter grade keys associated with an array of grade versions. Each array element consists of the text of the USPSTF recommendation for that grade and version. The following is a JavaScript code example of a grade look up using a specific recommendation:
var recom = results.specificRecommendations[0];
var gradeText = results.grades[recom.grade][recom.gradeVer];

## General Recommendations
The generalRecommendations object consists of integer keys associated with a general recommendation object. The specific
recommendation is targeted at a population. The general recommendation is broader. The following is an example of the general recommendation look up for a specific recommendation:
var recom = results.specificRecommendations[0];
var general = results.generalRecommendations[recom.general];

The following are the generalRecommendations fields:
* topicType: topic type in string - this is an " and " concatenated string 
* topicYear: topic year as an integer
* uspstfAlias: usptsf alias to reference the uspstf page
* specific: Array of integers identifying specific recommendations associated with this general recommendation
* title: title string
* pathwayToBenefit: pathway to benefit text string
* rationale (optional): HTML format - rationale for this recommendation. If rationale is not defined at the general level, display the specific rationale instead.
* clinical: HTML format - text of the clinical consideration
* clinicalUrl (optional, deprecated): URL associated with the clinical consideration - deprecated in favor of https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/<uspstfAlias>
* discussion (optional): HTML format - text of discussion
* other (optional): HTML format - other recommendation text - deprecated in favor of https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/<uspstfAlias>
* otherUrl (optional, deprecated): URL associated with the other recommendation text - deprecated in favor of https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/<uspstfAlias>
* topic: this recommendation's topic string
* keywords: a string of keywords list separated by '|' - used for search
* pubDate: date string of publication on USPSTF website (available after 2021-01) - YYYY-MM-DD format
* categories: an array of category id strings for indexing into the categories object
* tool: Array of tool id strings identifying tools associated with this general recommendation for indexing into the tools object. See Tools

uspstfAlias is used as a key for lookup up USPSTF recommendations on the USPSTF website.  For example: "https://www.uspreventiveservicestaskforce.org/uspstf/recommendation/" + generalRecommendations.123.uspstfAlias

## Tools
Tools are useful resources for a recommendation.  They were formerly linked directly to the specific recommendation for population targetting, but this is no longer maintained.  The Tool array is now at the general level, and echoed at the specific for legacy compatibility.
The format of the tools object is as follows.
1. If tools=y was provided, tools: [ {"key": "string" .. } .. ] - an array ordered by title for displaying a list of tools.
1. If tools=y was NOT provided, tools: { "key": {key: "string" .. } .. } - an object for indexing tools by id associated with a recommendation.

The fields for each tool are:
* id: number identifying this tool
* title: title string
* url: optional - URL string where the tool is located 
* text: HTML format - text describing the tool
* keywords: a string of keywords list separated by '|'

## Categories
The format of the categories object is as follows.
* categories: { "key": {key: "string" .. } .. } - an object for indexing categories by id associated with a specific recommendation.

## Risks
List of risks associated with populations. The code value is to offer a standard string for lookups.
The format of the risks object is as follows.
* risks: { "key": { code: "STRING", name: "string" } - an object for indexing risks by id associated with a specific recommendation.

## Sample Prevention TaskForce API Data Structure
```
{
    "specificRecommendations":
    [
        {
            "id": 1,
            "title": "<b>Sample Specific Recommendation</b>",
            "grade": "A",
            "gradeVer": 1,
            "sex": "male",
            "ageRange": [1,30],
            "text": "<br>Sample recommendation text",
            "rationale": "<p>Sample rationale</p>",
            "servFreq": "<p>Sample frequency of service</p>",
            "riskName": "Other",
            "risk": ["1","2","3"],
            "riskText": "<br>Sample risk",
            "general": "1",
            "tool": ["1"],
            "bmi": "O"
        }
    ],
    "grades":
    {
        "A": [
         "The USPSTF strongly recommends that clinicians provide [the service] to eligible patients. ",
         "The USPSTF recommends the service. There is high certainty that the net benefit is substantial. Offer or provide this service."
        ],
        "B": [
         "The USPSTF recommends that clinicians provide [the service] to eligible patients. ",
         "The USPSTF recommends the service."
        ],
        "C": [
         "The USPSTF makes no recommendation for or against routine provision of [the service]. ",
         "The USPSTF recommends against routinely providing the service."
        ],
        "I": [
         "The USPSTF concludes that the evidence is insufficient to recommend for or against routinely providing [the service]. ",
         "The USPSTF concludes that the current evidence is insufficient to assess the balance of benefits and harms of the service."
        ]
    },
    "generalRecommendations":
    {
        "1":
        {
            "topicType": "Screening and Counseling",
            "topicYear": "2020",
            "uspstfAlias": "sample-alias",
            "specific": [1],
            "title": "Sample title",
            "pathwayToBenefit": "Sample pathway to benefit",
            "rationale": "Sample rationale",
            "clinical": "<p>Sample clinical consideration</p>",
            "clinicalUrl": "http://localhost",
            "discussion": "<p>Sample discussion</p>",
            "other": "Sample other",
            "otherUrl": "http://localhost",
            "topic": "Sample topic",
            "keywords": "Keyword1|Keyword2|Keyword3",
            "pubDate": "2020-12-31",
            "categories": ["1","2"],
            "tool": ["1","2"]
        }
    },
    "tools":
    {
        "1":
        { 
            "url": "http://localhost",
            "title": "Sample title",
            "text": "Sample text",
            "keywords": "Keyword1|Keyword2|Keyword3"
        }
    },
    "categories":
    {
        "1":
        {
             "name": "Sample Category Name"
        }
    },
    "risks":
    {
        "0": 
        {
            code: "NONE",
            "None"
        },
        "1":
        {
            code: "TOBACCO",
            name: "Tobacco user"
        }
    }
}
```