import credentials
from openai import AzureOpenAI
from pprint import pprint




def transformdata(all_data):
    all_data = str(all_data)
    # change comma to space
    all_data = all_data.replace(',', ' ')
    #remove doublespaces
    all_data = all_data.replace('  ', ' ')
    # change : to space
    all_data = all_data.replace(':', ' ')
    #remove doublespaces
    all_data = all_data.replace('  ', ' ')
    #correct the https by adding back colon
    all_data = all_data.replace('https ', 'https:')
    # Remove quotes
    all_data = all_data.replace("'", '')
    # Remove brackets
    all_data = all_data.replace("[", '')
    # Remove brackets
    all_data = all_data.replace("]", '')
    # Remove brackets
    all_data = all_data.replace("{", '')
    # Remove double brackets
    all_data = all_data.replace('}}', '}')
    # change brackets to comma (this is the only logical seperator between list of items)
    all_data = all_data.replace("}", ',')
    # Remove space after comma
    all_data = all_data.replace(", ", ',')
    # Remove the last trailing comma
    all_data = all_data.rstrip(',')
    return all_data


def queryme(query,db):
    db_data = {}
    all_data = []
    for dbentry in db:
        for collection_name in dbentry.list_collection_names():
            if(collection_name == 'maindb-semantic'):
                continue
            collection = dbentry[collection_name]
            db_data[collection_name] = list(collection.find({}, {'_id': False}))
    all_data.append(db_data)
    #pprint(all_data)
    all_data = transformdata(all_data)
    with open("datanotes.txt", "r") as file:
        datanotes = file.read()
    all_data = str(all_data) + ";" + datanotes
    with open("runbook.txt", "r") as file:
        runbook = file.read().replace('\n', ' ')
        runbook = transformdata(runbook)
        # Create a chat completion
    messages = [
        {
            "role": "system",
            "content": f"Dashboard Data : {all_data}. Answer the user query with the given Dashboard Data. If the query cannot be answered with the dashboard data, politely mention that its not possible to answer with the dashboard data. Do not deviate from the dashboard data context and do not reply to any other unrelated queries. If the query asks for troubleshooting steps, do not give the steps but instead mention that it will be provided based on the runbook information."
        },
        {
            "role": "user",
            "content": query
        }
    ]

    # find the prompt token length
    prompt_length = int((len(str(messages))/4))
    print("prompt token length is: ", prompt_length)

    print("sending the prompt to the azuregtp4-o model")
    client = AzureOpenAI(
    azure_endpoint = "https://openaigpts.openai.azure.com/", 
    api_key=credentials.azure_openai_token,  
    api_version="2024-02-15-preview"
    )
    
    # Create a chat completion
    chat_completion = client.chat.completions.create(
        #model="azuregpt35turbo", messages = messages, temperature = 0.1, max_tokens = 1000
        model="azuregpt-4o", messages = messages, temperature = 0.1, max_tokens = 1000
    )

    # Print the assistant's message
    #print(messages[1],"\n", chat_completion.choices[0].message.content)
    #print("\n", chat_completion.choices[0].message.content)
    response1 = chat_completion.choices[0].message.content


    if(query.find("troubleshoot") != -1):
        messages = [
            {
                "role": "system",
                "content": "you are a helpful troubleshooting assistant"
            },
            {
                "role": "user",
                "content": f"Use this runbook information:'{runbook}' to provide any specific troubleshooting steps as applicable to the items mentioned in the Context : {response1}. Only mention the applicable troubleshooting steps from the runbook. If there are no runbook steps applicable, then mention 'No steps available in runbook for this'. Do not provide any steps outside of the given runbook."
            }
        ]

        # Create a chat completion
        chat_completion = client.chat.completions.create(
            #model="azuregpt35turbo", messages = messages, temperature = 0.1, max_tokens = 1000
            model="azuregpt-4o", messages = messages, temperature = 0.1, max_tokens = 1000
        )
        response2 = chat_completion.choices[0].message.content

        return f"{response1} \n {response2}"
    else:
        return response1
