from pymilvus import MilvusClient

client = MilvusClient(uri="http://localhost:19530")

# print(client.drop_collection("DOC_LEVEL"))

print(client.list_collections())
print(client.get_collection_stats("DOC_LEVEL"))
# print(client.describe_collection("DOC_LEVEL"))