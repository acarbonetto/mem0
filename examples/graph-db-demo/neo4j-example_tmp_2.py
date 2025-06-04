import logging, sys
from mem0 import Memory

logging.getLogger('mem0.memory.neptune_memory').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging.basicConfig(
    format='%(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout  # Explicitly set output to stdout
)

config = {
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "password"
        },
    },
    "vector_store": {
        "provider": "opensearch",
        "config": {
            "collection_name": "neo4j_vector_store",
            "host": "localhost",
            "port": 9200,
            "user": "admin",
            "password": "acarbonettoA1!",
            "use_ssl": False,
            "verify_certs": False,
        },
    },
    # "embedder": {
    # configure Neptune Analytics?
    # },
    # "llm": {
    #     "provider": "aws_bedrock",
    #     "config": {
    #         "model": "anthropic.claude-3-5-haiku-20241022-v1:0",
    #         "temperature": 0.2,
    #         "max_tokens": 2000,
    #     },
    # },
}

logger.debug(
    "---------------------------------------------------config_dict-------------------------------------------------"
)
m = Memory.from_config(config_dict=config)

messages = [
    {
        "role": "user",
        "content": "I'm planning to watch a movie tonight. Any recommendations?",
    },
    {
        "role": "assistant",
        "content": "How about a thriller movies? They can be quite engaging.",
    },
    {
        "role": "user",
        "content": "I'm not a big fan of thriller movies but I love sci-fi movies.",
    },
    {
        "role": "assistant",
        "content": "Got it! I'll avoid thriller recommendations and suggest sci-fi movies in the future.",
    },
]

# Store inferred memories (default behavior)
logger.debug(
    "---------------------------------------------------Add messages-------------------------------------------------"
)
result = m.add(
    messages, user_id="alice", metadata={"category": "movie_recommendations"}
)

# Store raw messages without inference
# result = m.add(messages, user_id="alice", metadata={"category": "movie_recommendations"}, infer=False)

# Get all memories
logger.debug(
    "---------------------------------------------------all_memories-------------------------------------------------"
)
all_memories = m.get_all(user_id="alice")
logger.debug(f"all_memories={all_memories}")


logger.debug(
    "---------------------------------------------------specific_memory-------------------------------------------------"
)
first_id = all_memories["results"][0]["id"]
specific_memory = m.get(first_id)
logger.debug(f"specific_memory={specific_memory}")


logger.debug(
    "---------------------------------------------------related_memories-------------------------------------------------"
)
related_memories = m.search(query="What do you know about me?", user_id="alice")
logger.debug(f"related_memories={related_memories}")

logger.debug(
    "---------------------------------------------------update-------------------------------------------------"
)
result = m.update(
    memory_id=first_id,
    data="I love India, it is my favorite country.",
)
logger.debug(f"m.update result={result}")

logger.debug(
    "---------------------------------------------------history-------------------------------------------------"
)
history = m.history(memory_id=first_id)
logger.debug(f"m.history={history}")

# Delete a memory by id
# print(
#     "---------------------------------------------------delete one-------------------------------------------------"
# )
# m.delete(memory_id=first_id)

# Delete all memories for a user
logger.debug(
    "---------------------------------------------------delete all by user-------------------------------------------------"
)
m.delete_all(user_id="alice")

logger.debug(
    "---------------------------------------------------reset-------------------------------------------------"
)
m.reset()  # Reset all memories
