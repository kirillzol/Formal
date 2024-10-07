from src.methods import *

"""
        В качестве тестового примера
            возьмем номер 2а из 2-го дз
"""

Q = [0, 1, 2, 3]
Sigma = ['a', 'b']
Delta = [(0, 1, {'w': ['a']}), (1, 1, {'w': ['b']}), (1, 2, {'w': ['a']}), (2, 2, {'w': ['ab']}),
         (2, 3, {'w': ['a']}), (3, 3, {'w': ['ab']}), (3, 1, {'w': ['1']})]
q0 = 0
F = [1]


def test_methods():
    A = Automaton(Q, Sigma, Delta, q0, F)

    A = delete_multi_letter_transitions(A)
    counter = 0
    for transition in A.Delta:
        for tr in transition[2]['w']:
            if len(tr) > 1:
                counter += 1
    assert counter == 0
    assert len(A.Q) == 6

    A = remove_epsilon_transitions(A)

    counter = 0
    for transition in A.Delta:
        for tr in transition[2]['w']:
            if len(tr) > 1 or tr == '1':
                counter += 1
    assert counter == 0
    assert len(A.Q) == 6

    A = complete_and_determinize(A)
    for q in A.Q:
        c = 0
        for transition in A.Delta:
            if transition[0] == q:
                c += len(transition[2]['w'])
        assert c == len(A.Sigma)
        assert len(A.Q) == 11

    A = minimization(A)
    assert len(A.Q) == 9
