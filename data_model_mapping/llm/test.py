import json
import boto3

# Initialize the Bedrock client
bedrock = boto3.client(service_name="bedrock-runtime")

# Define the explain request
explain_request = 'NO.1 G/E H.T WATER OUTLET TEMP'

# Define the body for the inference configuration
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

# Invoke the model
response = bedrock.invoke_model(
    modelId="anthropic.claude-v2",
    contentType="application/json",
    accept="application/json",
    body=json.dumps(body)
)

# Check the status code
status_code = response['ResponseMetadata']['HTTPStatusCode']
if status_code == 200:
    # Read and decode the response body
    response_body = json.loads(response['body'].read().decode('utf-8'))
    
    # Extract the generated text
    if 'completion' in response_body:
        generated_text = response_body['completion']
        print("Generated text:", generated_text)
        
        # Try to parse the generated text as JSON
        try:
            haikus = json.loads(generated_text)
            print(json.dumps(haikus, indent=2))
        except json.JSONDecodeError:
            print("Failed to parse the generated text as JSON. Here is the raw text:")
            print(generated_text)
    else:
        print("Key 'completion' not found in the response.")
else:
    print(f"Error: Received status code {status_code}")
