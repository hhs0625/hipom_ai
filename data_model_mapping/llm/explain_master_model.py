import json
import boto3
import pandas as pd
import os

# Initialize the Bedrock client
bedrock = boto3.client(service_name="bedrock-runtime")

# Read the master_desc.csv file
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_desc.csv')
df = pd.read_csv(csv_path)

# Function to call the Bedrock API
def call_bedrock_api(explain_request):
    body = {
        "prompt": (
            f"Human: I am reading ship's io list. Explain '{explain_request}' by 1 line.\n\nAssistant:\n"
        ),
        "max_tokens_to_sample": 2048,
        "temperature": 0.5,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman:"]
    }
    
    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )
    
    status_code = response['ResponseMetadata']['HTTPStatusCode']
    if status_code == 200:
        response_body = json.loads(response['body'].read().decode('utf-8'))
        if 'completion' in response_body:
            return response_body['completion']
        else:
            print("Key 'completion' not found in the response.")
            return None
    else:
        print(f"Error: Received status code {status_code}")
        return None

# Loop through the DataFrame and call the API
total_rows = len(df)
completed_rows = 0

for index, row in df.iterrows():
    explain_request = row['tag_description']
    response = call_bedrock_api(explain_request)
    if response:
        df.at[index, 'desc'] = response
        completed_rows += 1
        print(f"Row {index} updated")
        print(f"Request: {explain_request}")
        print(f"Response: {response}")
        print(f"Completed {completed_rows} out of {total_rows}\n")

# Save the updated DataFrame to the original CSV file
df.to_csv(csv_path, index=False)

print(f"Updated DataFrame has been saved to {csv_path}")
