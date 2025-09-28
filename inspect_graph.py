import json, collections, sys

path = sys.argv[1] if len(sys.argv) > 1 else "out/graph.json"
g = json.load(open(path, "r", encoding="utf-8"))

types = collections.Counter(n.get("type","") for n in g["nodes"])
print("Node type histogram:")
for k,v in types.most_common():
    print(f"  {k:15s} {v}")

print("\nSample non-ENDPOINT nodes with attrs:")
for n in g["nodes"]:
    if n.get("type") != "ENDPOINT":
        print({k:n[k] for k in ("id","type","attrs")})
        break

print("\nEdge kind histogram:")
kinds = collections.Counter(e["attrs"].get("kind","") for e in g["edges"])
for k,v in kinds.most_common():
    print(f"  {k:15s} {v}")
