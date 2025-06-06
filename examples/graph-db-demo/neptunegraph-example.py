import logging, sys, os
from mem0 import Memory
from langchain_aws import NeptuneAnalyticsGraph

# logging.getLogger('mem0.memory.neptune_memory').setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# logging.getLogger('boto3').setLevel(logging.WARNING)
# logging.getLogger('botocore').setLevel(logging.WARNING)

logging.basicConfig(
    format="%(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,  # Explicitly set output to stdout
)


def get_all_relationships():
    neptune_graph = NeptuneAnalyticsGraph(graph_identifier)

    query = """
            MATCH (n {user_id: $user_id})-[r]->(m {user_id: $user_id})
            RETURN n.name AS source, type(r) AS relationship, m.name AS target
            LIMIT $limit
            """
    edge_results = neptune_graph.query(query, params={"user_id": "alice", "limit": 100})

    print("----RELATIONSHIPS----")
    for e in edge_results:
        print(f"edge \"{e["source"]}\" --{e["relationship"]}--> \"{e["target"]}\"")

    query = """
    MATCH (n {user_id: $user_id})
    CALL neptune.algo.vectors.get(n)
    YIELD embedding
    RETURN n AS node, embedding
    LIMIT $limit
    """

    node_results = neptune_graph.query(query, params={"user_id": "alice", "limit": 100})
    # print(f"node_results={node_results}")

    print("----NODES----")
    for n in node_results:
        has_embedding = n.get("embedding", None) is not None
        print(f"node name:\"{n["node"]["~properties"]["name"]}\" embedding: {has_embedding}")


print(f"profile = {os.environ.get("AWS_PROFILE")}")
graph_identifier = os.environ.get("GRAPH_ID")
print(f"graph_identifier = {graph_identifier}")
opensearch_username = os.environ.get("OS_USERNAME")
opensearch_password = os.environ.get("OS_PASSWORD")

config = {
    "embedder": {
        "provider": "openai",
        "config": {"model": "text-embedding-3-large", "embedding_dims": 1536},
    },
    "graph_store": {
        "provider": "neptune",
        "config": {
            "endpoint": f"neptune-graph://{graph_identifier}",
        },
    },
    "vector_store": {
        "provider": "opensearch",
        "config": {
            "collection_name": "vector_store",
            "host": "localhost",
            "port": 9200,
            "user": opensearch_username,
            "password": opensearch_password,
            "use_ssl": False,
            "verify_certs": False,
        },
    },
}

logger.debug(
    "---------------------------------------------------config_dict-------------------------------------------------"
)
m = Memory.from_config(config_dict=config)
m.reset()
# only works for neptune_memory
memory_graph = m.graph.reset()

messages = [
    {
        "role": "user",
        "content": "I'm planning to watch a movie tonight. Any recommendations?",
    },
]

# Store inferred memories (default behavior)
logger.debug('--------USER: "I\'m planning to watch a movie tonight. Any recommendations?"')
result = m.add(messages, user_id="alice", metadata={"category": "movie_recommendations"})

get_all_relationships()

messages = [
    {
        "role": "assistant",
        "content": "How about a thriller movies? They can be quite engaging.",
    },
]

logger.debug('--------ASSISTANT: "How about a thriller movies? They can be quite engaging."')
# Store raw messages without inference
result = m.add(messages, user_id="alice", metadata={"category": "movie_recommendations"}, infer=False)

get_all_relationships()

messages = [
    {
        "role": "user",
        "content": "I'm not a big fan of thriller movies but I love sci-fi movies.",
    },
]

logger.debug('--------USER: "I\'m not a big fan of thriller movies but I love sci-fi movies."')
# Store raw messages without inference
result = m.add(messages, user_id="alice", metadata={"category": "movie_recommendations"}, infer=False)

get_all_relationships()

messages = [
    {
        "role": "assistant",
        "content": "Got it! I'll avoid thriller recommendations and suggest sci-fi movies in the future.",
    },
]

logger.debug(
    '--------ASSISTANT: "Got it! I\'ll avoid thriller recommendations and suggest sci-fi movies in the future."'
)
# Store raw messages without inference
result = m.add(messages, user_id="alice", metadata={"category": "movie_recommendations"}, infer=False)

get_all_relationships()

# Get all memories
# logger.debug(
#     "---------------------------------------------------all_memories-------------------------------------------------"
# )
# all_memories = m.get_all(user_id="alice")
# logger.debug(f"all_memories={all_memories}")


# logger.debug(
#     "---------------------------------------------------specific_memory-------------------------------------------------"
# )
# first_id = all_memories["results"][0]["id"]
# specific_memory = m.get(first_id)
# logger.debug(f"specific_memory={specific_memory}")


# logger.debug(
#     "---------------------------------------------------related_memories-------------------------------------------------"
# )
# related_memories = m.search(query="What do you know about me?", user_id="alice")
# logger.debug(f"related_memories={related_memories}")

# logger.debug(
#     "---------------------------------------------------update-------------------------------------------------"
# )
# result = m.update(
#     memory_id=first_id,
#     data="I love India, it is my favorite country.",
# )
# logger.debug(f"m.update result={result}")
#
# logger.debug(
#     "---------------------------------------------------history-------------------------------------------------"
# )
# history = m.history(memory_id=first_id)
# logger.debug(f"m.history={history}")

# Delete a memory by id
# print(
#     "---------------------------------------------------delete one-------------------------------------------------"
# )
# m.delete(memory_id=first_id)

# Delete all memories for a user
# logger.debug(
#     "---------------------------------------------------delete all by user-------------------------------------------------"
# )
# m.delete_all(user_id="alice")
#
# logger.debug(
#     "---------------------------------------------------reset-------------------------------------------------"
# )
# m.reset()  # Reset all memories
