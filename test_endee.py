from endee import Endee, Precision
from sentence_transformers import SentenceTransformer

client = Endee(token="l3uo1dzs:CQ2xTA7sKCMX9n6X6A7Ey1BOR37zaaUC:as1")


model = SentenceTransformer("all-MiniLM-L6-v2")

# Create index
try:
    client.create_index(
        name="resume_index",
        dimension=384,
        space_type="cosine",
        precision=Precision.INT8
    )
    print("Resume index created")
except:
    print("Resume index already exists")

index = client.get_index("resume_index")


# Sample resumes
resumes = [
    {
        "id": "1",
        "text": "Python developer skilled in machine learning, NLP, and data analysis using TensorFlow and PyTorch."
    },
    {
        "id": "2",
        "text": "Frontend developer experienced in React, JavaScript, CSS, and UI/UX design."
    },
    {
        "id": "3",
        "text": "Backend engineer with Java, Spring Boot, microservices, and database optimization experience."
    },
    {
        "id": "4",
        "text": "AI engineer with experience in LLMs, semantic search, embeddings, and vector databases."
    }
]

# Insert resumes
for resume in resumes:
    vector = model.encode(resume["text"]).tolist()

    index.upsert([{
        "id": resume["id"],
        "vector": vector,
        "meta": {"resume": resume["text"]}
    }])

print("Resumes inserted")


# Job description
job_description = """
Looking for an AI Engineer with experience in NLP,
machine learning, embeddings, and vector databases.
"""

query_vector = model.encode(job_description).tolist()

results = index.query(
    vector=query_vector,
    top_k=3
)

print("\nTop Matching Candidates:\n")

for i, match in enumerate(results, start=1):
    print(f"{i}. Score:", match.get("score"))
    print("   Resume:", match.get("meta", {}).get("resume"))