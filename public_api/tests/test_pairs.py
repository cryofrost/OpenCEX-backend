from rest_framework import status

from core.pairs import PAIRS_LIST
from .client import Client


PAIRS_URL = '/api/public/v1/markets'


def test_pairs():
    c = Client()

    res = c.get(PAIRS_URL)
    assert res.status_code == status.HTTP_200_OK

    # pairs = res.json().get('pairs')
    print(res.json())
    pairs = res.json()

    assert len(PAIRS_LIST) == len(pairs)
