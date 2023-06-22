import requests
import numpy as np
import pandas as pd
from os import getenv
from typing import Callable
from dotenv import load_dotenv
load_dotenv()


df = pd.read_pickle('control_embeddings.pkl')
embeddings = np.array(df['vector'].to_list())


def embed_fn(text: list[str]) -> np.ndarray:
    auth = getenv('OPENAI_API_KEY')
    response = requests.post(
        'https://api.openai.com/v1/embeddings',
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {auth}',
        },
        json={
            'input': text,
            'model': 'text-embedding-ada-002',
        },
    ).json()
    return np.array(
        [i['embedding'] for i in response['data']]
    )


def top_k(vec: np.array, k: int) -> list[int]:
    return list(np.argpartition(vec, k)[-k:])


def cosine_similarity(a: np.array, b: np.array):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def search_embeddings(
        query: str,
        embed_fn: Callable = embed_fn,
        limit: int = 3,
) -> list[str]:
    q_embed = embed_fn(query)
    return df['text'].iloc[top_k(
        cosine_similarity(embeddings, q_embed.reshape(-1)),
        limit,
    )].to_list()
