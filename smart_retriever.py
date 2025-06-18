from chroma_manager import search_chapters
from rl_search_agent import RLSearchAgent

agent = RLSearchAgent()

def rl_search(query, top_k=5):
    search_results = search_chapters(query, k=top_k*2)
    if not search_results:
        return []  # 🛑 No documents found

    doc_ids = [doc_id for doc_id, _, _ in search_results]
    chosen_docs = []
    state = query.lower().strip()

    for _ in range(min(top_k, len(doc_ids))):
        action = agent.choose_action(state, doc_ids)
        if action is None:
            continue
        chosen_docs.append(action)
        doc_ids.remove(action)

    return [doc for doc in search_results if doc[0] in chosen_docs]

def feedback(query, chosen_id, reward):
    state = query.lower().strip()
    next_state = state  # stateless example
    possible_actions = []  # assume top docs are same for now
    agent.update(state, chosen_id, reward, next_state, possible_actions)
