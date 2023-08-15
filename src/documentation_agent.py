import os
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import (
    create_vectorstore_router_agent,
    VectorStoreRouterToolkit,
    VectorStoreInfo,
)
# from om_embeddings import embed_fn, db

load_dotenv()


# vectorstore = VectorStoreInfo(
#     name='Modelica Standard Library',
#     description='information about components, models, and example simulations for system dynamics and control. Simply use keywords to search for components or browse the Modelica Standard Library.',
#     vectorstore=db,
# )

# llm = ChatOpenAI(
#     model_name='gpt-3.5-turbo-16k',
#     # model_name='gpt-4-0613',
#     temperature=0.0,
# )

# from langchain.chains import RetrievalQA
# from langchain.agents import initialize_agent, Tool, AgentType
# tools = [
#     Tool(
#         name='Modelica Standard Library',
#         description='information about components, models, and example simulations for system dynamics and control. Input MUST be a fully-formed question.',
#         func=RetrievalQA.from_chain_type(
#             llm=llm,
#             chain_type='stuff',
#             retriever=db.as_retriever(search_kwargs=dict(k=3)),
#         )
#     ),
# ]
# agent_executor = initialize_agent(
#     tools,
#     llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
#     return_intermediate_steps=True,
# )

# router_toolkit = VectorStoreRouterToolkit(
#     vectorstores=[vectorstore],
#     llm=llm,
# )

# agent_executor = create_vectorstore_router_agent(
#     llm=llm,
#     toolkit=router_toolkit,
#     verbose=True,
#     max_iterations=10,
#     return_intermediate_steps=True,
# )




def modelica_documentation_lookup(search_query):
    from om_embeddings import embed_fn, db
    retriever = db.as_retriever(
        # search_type='similarity_score_threshold',
        search_kwargs=dict(
            k=1,
            # score_threshold=0.1,
        ),
    )


    def format(doc):
        source = doc.metadata['source'].replace('data/', '')
        return f'{source}:\n{doc.page_content}'

    return '\n\n'.join([
        format(doc)
        for doc in retriever.get_relevant_documents(search_query)
    ])


# def consult_modelica_documentation(search_query):
#     docs = retriever.get_relevant_documents(search_query)
#     header = f'Your goal is to research the available documentation to find the most relevant information for writing a program that achieves the following objective: {search_query}. Your intended audience is an expert developer, so adjust your tone and included information accordingly. Summarize the intended purpose and key features IN A SINGLE PARAGRAPH of the following excerpt from the Modelica documentation:\n'
#     summaries = [
#         llm.predict(header + doc.page_content) for doc in docs
#     ]
#     combined = '\n\n'.join([
#         f'{doc.page_content}\nSUMMARY: {summary}'
#         for doc, summary in zip(docs, summaries)
#     ])
#     return combined

#     # search_query = search_query.replace('Search for', '')
#     # response = agent_executor({'input': header + search_query})
#     # import pdb; pdb.set_trace()
#     # return f"{response['intermediate_steps']}\n{response['output']}"
#     # # with io.StringIO() as buf, redirect_stdout(buf):
#     #     final_output = agent_executor(search_query)
#     #     chain = buf.getvalue()
#     # return f'{chain}\n\nRESULT:\n{final_output}\n\n'


if __name__ == '__main__':
    while True:
        print('> ', end='')
        # print(consult_modelica_documentation(input()))
        print(modelica_documentation_lookup(input()))
        print('\n---\n')
