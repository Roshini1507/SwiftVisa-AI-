import google.generativeai as genai
from config.config import VECTORSTORE_PATH
from langchain_community.vectorstores import FAISS
from prompt import ELIGIBILITY_PROMPT
from models.llm import generate_response
from utils.web_search import search_web
from models.embeddings import load_embedding_model
embeddings = load_embedding_model()

# Load FAISS vector store
VECTORSTORE_PATH = "vectorstore"
vectorstore = FAISS.load_local(
    VECTORSTORE_PATH,
    embeddings,
    allow_dangerous_deserialization=True
)

    
def retrieve_context(country, visa_type, query_text):
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 5,
            "filter": {
                "country": country.upper(),
                "visa_type": visa_type.upper()
            }
        }
    )

    try:
        docs = retriever.invoke(query_text)
    except Exception as e:
        print("Retriever error:", e)
        docs = []

    context = "\n\n".join([doc.page_content for doc in docs])

    return context,docs


def generate_eligibility(user_profile,response_mode="detailed"):

    query_text = f"""
    Evaluate eligibility for {user_profile['visa_type']} visa in {user_profile['country']}
    """

    context, docs = retrieve_context(
        country=user_profile["country"],
        visa_type=user_profile["visa_type"],
        query_text=query_text
    )
    
    web_context =""
    # If RAG context is weak, fetch web results

    if not context or len(context.strip()) < 200:

        print("RAG context weak → using web search")
        web_context = search_web(query_text)


    if response_mode == "concise":
        response_instruction = """
        Provide a short summarized answer.

        STRICT FORMAT:

        Eligibility Status:
        Short Explanation:
        Confidence Score (0-100%):

        Explanation must be 2–3 sentences only.
        Do NOT include Policy References or Missing Information.
        """
    else:
        response_instruction = """
        Provide a detailed explanation.

        Return in this format:

        Eligibility Status:
        Explanation:
        Policy References:
        Missing Information:
        Confidence Score:
        """
    prompt = ELIGIBILITY_PROMPT.format(
        age=user_profile["age"],
        nationality=user_profile["nationality"],
        education=user_profile["education"],
        employment=user_profile["employment"],
        income=user_profile["income"],
        country=user_profile["country"],
        visa_type=user_profile["visa_type"],
        context=context,
        web_context=web_context,
        response_mode_instruction=response_instruction
    )

    try:
        response = generate_response(prompt)
        return response, docs

    except Exception as e:
        return f"LLM Error: {str(e)}", []
    