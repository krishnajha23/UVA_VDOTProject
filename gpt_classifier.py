import pandas as pd
import openai
import tiktoken
import time
#VDOT Notebook: https://colab.research.google.com/drive/1PlH7QIQ9H2jZIWHJIwhoHID1-Jpn1wzd#scrollTo=K0GSpBtGlmjo
#Microsoft excel book link: https://myuva.sharepoint.com/:x:/r/sites/VDOT/_layouts/15/doc2.aspx?sourcedoc=%7B3ac920b5-ac42-42eb-bc77-e28d19e91889%7D&action=edit&activeCell=%27LLMRuns%27!A1&wdinitialsession=2af0f672-8f11-42b5-8ed8-c15100bdfed9&wdrldsc=2&wdrldc=1&wdrldr=AccessTokenExpiredWarning%2CRefreshingExpiredAccessT 
#ChatGPT link: https://chat.openai.com/c/dd769d85-98a4-4ff7-ba11-33255dff9e32
#Non-routine = corrective and major = significant
#Try shortening context paragraph
#Can we tell the model to choose more severe events if its struggling to categorize something?
#Ex: if in between routine/corrective, pick corrective since it's more severe
#Routine < corrective < significant
#Run 20 on longer prompt, then run 20 on shortened prompt, and then run 20 asking chatgpt to use its knowledge
#Keep experimenting with stuff like sleep time, timeout, etc.
#Shortened prompt can be: Based on your knowledge of stormwater BMPs, categorize routine, corrective, significant, or unknown. Only supply one of those words.
'''
This is his response: Savannah, since I don’t have access to HMMS, I don’t know how the software or data entries typically describe various
levels of maintenance. From my perspective, Routine Maintenance involves the kinds of things you described in your description.
But, in reality, everything beyond that is actually Non-Routine, so I usually avoid using that term. My second level term is Corrective
Maintenance, which means that minor structural repairs, sediment removal, etc., much as you described, must be done. I call my third/worst
category Significant Maintenance, but your Major Maintenance works as well. Otherwise, I think you have described the three layers correctly.
'''
thedf = pd.read_excel(r'comparing_runs_with_final_results.xlsx', skiprows=1)[['Description','BMP Maintenance Type']].dropna()
thedf = thedf[thedf['BMP Maintenance Type'] != 'Non-routine']
thedf = thedf[thedf['BMP Maintenance Type'] != 'Major']
thedf = thedf.head(7)
openai.api_key = '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'
column_name = 'Description'
context_paragraph = """
Maintenance tasks are classified into three categories: Routine, Corrective, and Significant.
Routine maintenance involves regular activities like conducting an annual inspection, managing
vegetation and ground cover, and removing any litter. Routine Maintenance is typically related
to Inspection, Mowing, Trimming, Spraying, and Clean-up. Corrective maintenance are structural
repairs, erosion-related issues, and clearing sediment and debris to prevent blockages and damage.
Corrective Maintenance is Sediment Removal, Shrub or Tree Removal, Erosion Repair, or Structural
Repair. Significant maintenance denotes restoration, rehabilitation, and rebuilding, and it is
extremely costly repair. If the description is unclear, nonexistent or does not fall into any of
these categories, then categorize it as Unknown. ONLY respond with one of the four categories,
leave out all descriptors and only supply one of the following words: Routine, Corrective, Significant, or Unknown.
"""


if column_name in thedf.columns:
    column_values = thedf[column_name].tolist()

    # Initialize a list to store categorized results
    #categorized_results = {}
    categorized_results = []

    # Iterate through the values in the column
    for value in column_values:

        # The data you want to categorize
        data_to_categorize = value

        try:
            # Make an API request to OpenAI with the value as input
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"{context_paragraph}\nCategorize the following:\n{data_to_categorize}\nCategory: "}
                ],
                timeout = 12000
            )
            # Extract the categorization result from the model's response
            #print(value)
            category = response['choices'][0]['message']['content'].strip()
            #print(category)
            # Store the categorized result in the dictionary
            categorized_results.append(category)
            print(categorized_results)
            # Introduce a delay of 2 seconds between requests
            time.sleep(2)
        except Exception as e:
            print(f"Error processing value '{value}': {e}")

    # Save the categorized results to a new Excel file
    #categorized_df = pd.DataFrame(list(categorized_results.items()), columns=['Description', 'Determination'])
    #categorized_df.to_excel(r'C:\Users\savan\OneDrive - University of Virginia\VDOT_Chat_GPT\categorized_results.xlsx', index=False)


else:
    print(f"Column '{column_name}' not found in the Excel file.")
thedf['LLM'] = categorized_results
correctanswers = 0
total = len(thedf)
for i in thedf.iterrows():
  llm = i[1]['LLM']
  correct = i[1]['BMP Maintenance Type']
  if llm == correct:
    correctanswers += 1
percentsimilarity = correctanswers/total
print("Percent similarity between LLM and final: ", percentsimilarity*100, "%")
