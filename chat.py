import subprocess,json

def query_ollama(prompt,model="mistral"):
    try:
        cmd = ["ollama","run",model]
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,text= True)
        output,_ = process.communicate(prompt)
        return output
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    response = query_ollama("What is 2+2?", model="mistral")
    print(response)

def generate_answer(context,question,model="mistral"):
    """"
    Combines extracted text(content) and user question into a structured prompt,
    sends it to Ollama and returns the models answer.
    """
    prompt = f'''
    You are a financial assistance. Use the following financial data to answer the questions. 
    Financial Document Text:
    {context[:4000]}   # Limit to avoid too-long text for small models

    Question:
    {question}

    Answer clearly and concisely, using only the given data.
    '''
    return query_ollama(prompt,model)
