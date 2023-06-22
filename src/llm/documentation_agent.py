import lancedb
from requests import get as GET
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import LanceDB
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_toolkits import (
    create_vectorstore_router_agent,
    VectorStoreRouterToolkit,
    VectorStoreInfo,
)


load_dotenv()


embed = OpenAIEmbeddings()
db = lancedb.connect('/tmp/lancedb')

if 'control' not in db.table_names():
    print('Creating Python Control Library embeddings...')
    # res = GET(
    #     'https://python-control.readthedocs.io/_/downloads/en/0.9.2/pdf/'
    # )
    # with open('/tmp/control.pdf', 'wb') as f:
    #     f.write(res.content)

    loader = PyPDFLoader('/tmp/control.pdf')
    docs = loader.load_and_split()
    docs = docs[13:124]

    table = db.create_table(
        'control',
        data=[{
            'vector': embed.embed_query('dummy'),
            'text': 'dummy',
            'id': '1',
        }],
        mode='overwrite',
    )
    db = LanceDB.from_documents(docs, embed, connection=table)
else:
    table = db.open_table('control')
    db = LanceDB(table, embed)


vectorstore = VectorStoreInfo(
    name='Python Control Library Documentation',
    description='questions about control systems, systems modeling, etc',
    vectorstore=db,
)

llm = ChatOpenAI(
    model_name='gpt-3.5-turbo-0613',
    # model_name='gpt-4-0613',
    temperature=0.0,
)

router_toolkit = VectorStoreRouterToolkit(
    vectorstores=[vectorstore],
    llm=llm,
)

agent_executor = create_vectorstore_router_agent(
    llm=llm,
    toolkit=router_toolkit,
    verbose=True,
    max_iterations=5,
)


def consult_control_documentation(search_query):
    return agent_executor.run(search_query)
