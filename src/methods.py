from src.auto import *
from collections import deque


def compare(A: Automaton):
    sorted(A.Delta, key=lambda x: (x[0], x[1]))
    new_delta = [A.Delta[0]]

    for (start, end, trans_info) in A.Delta[1:]:
        if (new_delta[-1][0], new_delta[-1][1]) == (start, end):
            new_delta[-1][2]['w'] += trans_info['w']
            new_delta[-1][2]['w'] = list(set(new_delta[-1][2]['w']))
        else:
            new_delta.append((start, end, trans_info))

    A.Delta = new_delta
    return A


def delete_multi_letter_transitions(A: Automaton):
    new_states_counter = len(A.Q)
    new_delta = []

    for transition in A.Delta:
        start_state, end_state, trans_w = transition
        transition_words = trans_w['w']

        for transition_word in transition_words:
            if len(transition_word) > 1:
                current_state = start_state
                for i, symbol in enumerate(transition_word):
                    if i == len(transition_word) - 1:
                        new_delta.append((current_state, end_state, {'w': [symbol]}))
                    else:
                        new_state = new_states_counter
                        A.Q.append(new_state)
                        new_delta.append((current_state, new_state, {'w': [symbol]}))
                        current_state = new_state
                        new_states_counter += 1
            else:
                new_delta.append((start_state, end_state, {'w': [transition_word]}))

    A.Delta = new_delta
    A = compare(A)
    A.status = "НКА с не более чем однобуквенными переходами"
    return A


def epsilon_closure(A: Automaton):
    epsilon = '1'
    dict_of_epsilon_transitions = {state: {state} for state in A.Q}

    for state in A.Q:
        to_process = [state]
        while to_process:
            current_state = to_process.pop()
            for (start, end, trans_info) in A.Delta:
                if start == current_state and epsilon in trans_info['w']:
                    if end not in dict_of_epsilon_transitions[state]:
                        dict_of_epsilon_transitions[state].add(end)
                        to_process.append(end)

    return dict_of_epsilon_transitions


def remove_epsilon_transitions(A: Automaton):  # строим эпсилон замыкание

    A = delete_multi_letter_transitions(A)
    epsilon = '1'
    new_delta = []

    dict_of_epsilon_transitions = epsilon_closure(A)

    # стягиваем ребра

    for state in A.Q:
        for eps_state in dict_of_epsilon_transitions[state]:
            for transition in A.Delta:
                if transition[0] == eps_state and epsilon not in transition[2]['w']:
                    new_delta.append((state, transition[1], transition[2]))

    for state in A.Q:
        for i in dict_of_epsilon_transitions[state]:
            if i in A.F and state not in A.F:
                A.F.append(state)

    A.F = sorted(A.F)
    A.Q = sorted(A.Q)

    A.Delta = [transition for transition in new_delta if epsilon not in transition[2]['w']]  # удаляем эпсилон переходы
    A.Delta = sorted(A.Delta)

    # нормируем

    dict_of_new_nodes = {}
    list_of_new = []
    for (start, end, trans_info) in A.Delta:
        if start not in list_of_new:
            list_of_new.append(start)
        if end not in list_of_new:
            list_of_new.append(end)

    list_to_del = set(A.Q) - set(list_of_new)
    list_to_del = list(list_to_del)

    j = 0

    for i in A.Q:
        if i in list_to_del:
            dict_of_new_nodes[i] = "del"
        else:
            dict_of_new_nodes[i] = j
            j += 1

    new_delta = []
    new_f = []
    for (start, end, trans_info) in A.Delta:
        new_delta.append((dict_of_new_nodes[start], dict_of_new_nodes[end], trans_info))

    for f in A.F:
        if dict_of_new_nodes[f] != "del":
            new_f.append(dict_of_new_nodes[f])

    A.Delta = new_delta
    A.Q = [i for i in range(0, len(list_of_new))]
    A.F = new_f
    A = compare(A)

    A.status = "НКА с однобуквенными переходами"

    return A


def find_factor(l: frozenset, A: Automaton, word: str):
    result = set()

    for (start, end, trans_info) in A.Delta:
        if start in l and word in trans_info['w']:
            result.add(end)

    return frozenset(result)


def complete_and_determinize(A):
    A = remove_epsilon_transitions(A)

    queue = deque()

    initial_state = frozenset([A.Q[0]])
    table = {initial_state: {"number": 0, "is_final": False, **{i: None for i in A.Sigma}}}
    queue.append(initial_state)

    iter = 0

    new_f = []
    while queue:
        current_state = queue.popleft()
        table[current_state]["number"] = iter

        if set(current_state) & set(A.F):
            table[current_state]["is_final"] = True
            new_f.append(iter)

        for symbol in A.Sigma:
            l = find_factor(current_state, A, symbol)
            l_frozenset = frozenset(l)

            if l_frozenset not in table:
                table[l_frozenset] = {"number": None, "is_final": False, **{i: None for i in A.Sigma}}
                queue.append(l_frozenset)

            table[current_state][symbol] = l_frozenset

        iter += 1

    new_q = [i for i in range(len(table))]

    new_delta = []

    for fs in table.keys():
        for symbol in A.Sigma:
            new_delta.append((table[fs]["number"], table[(table[fs])[symbol]]["number"], {'w': [symbol]}))

    A.Delta = new_delta
    A.Q = new_q
    A.F = new_f

    A = compare(A)

    A.status = "ПДКА"

    # print(table)
    # print(A.Delta)

    return A


def find_classes(K0: list, A: Automaton) -> (list, bool):
    new_delta = []
    K1 = []
    block = []
    dict_of_transitions = {i: [] for i in A.Sigma}

    for l in A.Sigma:
        for i in A.Q:
            for (start, end, trans_info) in A.Delta:
                if start == i and l in trans_info['w']:
                    dict_of_transitions[l].append(K0[end])
                    continue
    for i in A.Q:
        st = []
        for l in A.Sigma:
            st.append(dict_of_transitions[l][i])
        st = [K0[i]] + st
        block.append(st)

    dict_for_new_class = {}
    i = 0
    for st in block:

        if tuple(st) not in dict_for_new_class:
            dict_for_new_class[tuple(st)] = i
            i += 1

    for i in A.Q:
        K1.append(dict_for_new_class[tuple(block[i])])

    flag = (i == A.Q or len(set(K0)) == len(set(K1)))

    if flag:
        for st in block:
            (start, end, trans_info) = st[0], st[1], {'w': ['a']}
            new_delta.append((start, end, trans_info))
            (start, end, trans_info) = st[0], st[2], {'w': ['b']}
            new_delta.append((start, end, trans_info))

    return K1, flag, new_delta


def minimization(A):
    A = complete_and_determinize(A)

    K0 = []
    for q in A.Q:
        if q in A.F:
            K0.append(1)
        else:
            K0.append(0)

    while True:
        K1, flag, new_delta = find_classes(K0, A)
        if flag:
            break

        K0 = K1

    print(K1)

    A.Delta = new_delta
    A = compare(A)
    new_f = []
    for i in range(len(K1)):
        if i in A.F:
            new_f.append(K1[i])
    new_f = list(set(new_f))
    A.F = new_f
    A.Q = [i for i in set(K1)]
    A.status = "МПДКА"

    return A
