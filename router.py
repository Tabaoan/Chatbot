from typing import Any, Dict, Literal
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnableBranch

from chains import classify_chain, tavily_chain, vectordb_chain, general_chain

def choose_branch(r: Dict[str, Any]) -> Literal["troubleshoot","english_practice","general"]:
    label = r.get("label", "general")
    if label == "troubleshoot": return "troubleshoot"
    if label == "english_practice": return "english_practice"
    return "general"

add_route = RunnableLambda(lambda r: {**r, "route": choose_branch(r)})

router = RunnableBranch(
    (lambda i: i["route"] == "troubleshoot", tavily_chain),
    (lambda i: i["route"] == "english_practice", vectordb_chain),
    general_chain,  # default
)

def synth(i: Dict[str, Any]) -> str:
    return f"{i['payload']['answer']}\n\n_Source: {i['payload']['source']}_"

core_chain = (
    classify_chain
    | add_route
    | RunnableParallel(
        payload=router,
        passthrough=RunnableLambda(lambda x: x)
    )
    | RunnableLambda(lambda d: {"payload": d["payload"], **d["passthrough"]})
    | RunnableLambda(synth)
)
