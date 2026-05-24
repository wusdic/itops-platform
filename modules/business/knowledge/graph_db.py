"""
知识图谱引擎
实现两种模式：
1. Neo4jDriver: 真实 Neo4j 连接（需要 Neo4j 服务）
2. InMemoryGraphDB: 内存图数据库（完全自包含，无需外部依赖）

提供统一的图查询接口，支持：
- 节点 CRUD
- 关系 CRUD
- 图遍历（BFS/DFS）
- 模式匹配查询
- 故障案例相似度传播
"""

import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class NodeLabel(str, Enum):
    """节点标签枚举"""
    FAULT_CASE = "FaultCase"       # 故障案例
    DEVICE = "Device"               # 设备
    SYMPTOM = "Symptom"            # 症状现象
    CAUSE = "Cause"                # 故障原因
    SOLUTION = "Solution"          # 解决方案
    COMPONENT = "Component"        # 组件/服务
    ALERT = "Alert"                # 告警
    WORK_ORDER = "WorkOrder"       # 工单
    SOP = "SOP"                    # 标准操作程序


class RelType(str, Enum):
    """关系类型枚举"""
    SIMILAR_TO = "SIMILAR_TO"              # 相似案例
    CAUSED_BY = "CAUSED_BY"                # 由...引起
    RESOLVED_BY = "RESOLVED_BY"            # 由...解决
    AFFECTS = "AFFECTS"                    # 影响
    RELATES_TO = "RELATES_TO"              # 相关
    ESCALATED_FROM = "ESCALATED_FROM"      # 从...升级
    FOLLOWS_SOP = "FOLLOWS_SOP"           # 遵循SOP
    TRIGGERS = "TRIGGERS"                 # 触发


@dataclass
class GraphNode:
    """图节点"""
    id: str
    label: str
    properties: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "properties": self.properties,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class GraphRelationship:
    """图关系/边"""
    id: str
    start_node_id: str
    end_node_id: str
    type: str
    properties: dict = field(default_factory=dict)
    weight: float = 1.0  # 边的权重（用于相似度传播）
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "start_node_id": self.start_node_id,
            "end_node_id": self.end_node_id,
            "type": self.type,
            "properties": self.properties,
            "weight": self.weight,
            "created_at": self.created_at,
        }


class GraphDBInterface(ABC):
    """图数据库统一接口"""

    @abstractmethod
    def create_node(self, label: str, properties: dict) -> GraphNode:
        """创建节点"""
        pass

    @abstractmethod
    def get_node(self, node_id: str) -> Optional[GraphNode]:
        """获取节点"""
        pass

    @abstractmethod
    def update_node(self, node_id: str, properties: dict) -> Optional[GraphNode]:
        """更新节点"""
        pass

    @abstractmethod
    def delete_node(self, node_id: str) -> bool:
        """删除节点及其所有关系"""
        pass

    @abstractmethod
    def create_relationship(
        self, start_node_id: str, end_node_id: str,
        rel_type: str, properties: dict = None, weight: float = 1.0
    ) -> Optional[GraphRelationship]:
        """创建关系"""
        pass

    @abstractmethod
    def delete_relationship(self, rel_id: str) -> bool:
        """删除关系"""
        pass

    @abstractmethod
    def find_nodes(self, label: str, properties: dict = None, limit: int = 100) -> list[GraphNode]:
        """查找节点"""
        pass

    @abstractmethod
    def find_relationships(self, start_node_id: str = None, end_node_id: str = None,
                          rel_type: str = None) -> list[GraphRelationship]:
        """查找关系"""
        pass

    @abstractmethod
    def traverse_bfs(self, start_node_id: str, max_depth: int = 3,
                     rel_types: list[str] = None) -> list[dict]:
        """BFS 遍历"""
        pass

    @abstractmethod
    def traverse_dfs(self, start_node_id: str, max_depth: int = 3,
                     rel_types: list[str] = None) -> list[dict]:
        """DFS 遍历"""
        pass

    @abstractmethod
    def find_path(self, start_node_id: str, end_node_id: str,
                  max_depth: int = 5, rel_types: list[str] = None) -> Optional[list[dict]]:
        """查找两点间的路径"""
        pass

    @abstractmethod
    def similar_nodes(self, node_id: str, label: str = None, limit: int = 10) -> list[dict]:
        """查找相似节点（通过关系传播）"""
        pass

    @abstractmethod
    def close(self):
        """关闭连接"""
        pass


class InMemoryGraphDB(GraphDBInterface):
    """
    内存图数据库
    完全自包含，支持持久化到文件
    """

    def __init__(self, persist_path: str = None):
        self._nodes: dict[str, GraphNode] = {}
        self._rels: dict[str, GraphRelationship] = {}
        self._node_index: dict[str, dict[str, GraphNode]] = {}  # label -> {node_id -> node}
        self._rel_index: dict[str, list[GraphRelationship]] = {}  # (start, type, end) -> [rels]
        self._lock = threading.RLock()
        self._persist_path = persist_path
        if persist_path:
            self._load()

    def _gen_id(self) -> str:
        return str(uuid.uuid4())[:12]

    def _index_node(self, node: GraphNode):
        if node.label not in self._node_index:
            self._node_index[node.label] = {}
        self._node_index[node.label][node.id] = node

    def _unindex_node(self, node: GraphNode):
        if node.label in self._node_index:
            self._node_index[node.label].pop(node.id, None)

    def create_node(self, label: str, properties: dict) -> GraphNode:
        with self._lock:
            node = GraphNode(id=self._gen_id(), label=label, properties=properties)
            self._nodes[node.id] = node
            self._index_node(node)
            self._persist()
            return node

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self._nodes.get(node_id)

    def update_node(self, node_id: str, properties: dict) -> Optional[GraphNode]:
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                return None
            node.properties.update(properties)
            node.updated_at = time.time()
            self._persist()
            return node

    def delete_node(self, node_id: str) -> bool:
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                return False
            # 删除所有关联关系
            to_delete = [r.id for r in self._rels.values()
                        if r.start_node_id == node_id or r.end_node_id == node_id]
            for rid in to_delete:
                del self._rels[rid]
            self._unindex_node(node)
            del self._nodes[node_id]
            self._persist()
            return True

    def create_relationship(
        self, start_node_id: str, end_node_id: str,
        rel_type: str, properties: dict = None, weight: float = 1.0
    ) -> Optional[GraphRelationship]:
        with self._lock:
            if start_node_id not in self._nodes or end_node_id not in self._nodes:
                return None
            rel = GraphRelationship(
                id=self._gen_id(),
                start_node_id=start_node_id,
                end_node_id=end_node_id,
                type=rel_type,
                properties=properties or {},
                weight=weight,
            )
            self._rels[rel.id] = rel
            self._persist()
            return rel

    def delete_relationship(self, rel_id: str) -> bool:
        with self._lock:
            if rel_id in self._rels:
                del self._rels[rel_id]
                self._persist()
                return True
            return False

    def find_nodes(self, label: str, properties: dict = None, limit: int = 100) -> list[GraphNode]:
        with self._lock:
            nodes = list(self._node_index.get(label, {}).values())
            if properties:
                nodes = [
                    n for n in nodes
                    if all(n.properties.get(k) == v for k, v in properties.items())
                ]
            return nodes[:limit]

    def find_relationships(self, start_node_id: str = None, end_node_id: str = None,
                          rel_type: str = None) -> list[GraphRelationship]:
        with self._lock:
            result = list(self._rels.values())
            if start_node_id:
                result = [r for r in result if r.start_node_id == start_node_id]
            if end_node_id:
                result = [r for r in result if r.end_node_id == end_node_id]
            if rel_type:
                result = [r for r in result if r.type == rel_type]
            return result

    def traverse_bfs(self, start_node_id: str, max_depth: int = 3,
                     rel_types: list[str] = None) -> list[dict]:
        """BFS 遍历，返回路径列表"""
        with self._lock:
            if start_node_id not in self._nodes:
                return []
            visited = {start_node_id}
            queue = [(start_node_id, 0, [])]  # (node_id, depth, path)
            results = []

            while queue:
                node_id, depth, path = queue.pop(0)
                if depth >= max_depth:
                    continue

                node = self._nodes[node_id]
                # 找所有出边
                for rel in self._rels.values():
                    if rel.start_node_id != node_id:
                        continue
                    if rel_types and rel.type not in rel_types:
                        continue
                    neighbor = rel.end_node_id
                    if neighbor in visited:
                        continue
                    visited.add(neighbor)
                    new_path = path + [
                        {"type": "node", "data": node.to_dict()},
                        {"type": "rel", "data": rel.to_dict()},
                    ]
                    results.append({
                        "node": self._nodes[neighbor].to_dict(),
                        "depth": depth + 1,
                        "path": new_path,
                    })
                    queue.append((neighbor, depth + 1, new_path))

            return results

    def traverse_dfs(self, start_node_id: str, max_depth: int = 3,
                     rel_types: list[str] = None) -> list[dict]:
        """DFS 遍历"""
        with self._lock:
            visited = set()

            def dfs(node_id: str, depth: int, path: list) -> list[dict]:
                if depth >= max_depth or node_id in visited:
                    return []
                visited.add(node_id)
                results = [{"node": self._nodes[node_id].to_dict(), "depth": depth, "path": path}]

                for rel in self._rels.values():
                    if rel.start_node_id != node_id:
                        continue
                    if rel_types and rel.type not in rel_types:
                        continue
                    neighbor = rel.end_node_id
                    if neighbor not in visited:
                        new_path = path + [
                            {"type": "node", "data": self._nodes[node_id].to_dict()},
                            {"type": "rel", "data": rel.to_dict()},
                        ]
                        results.extend(dfs(neighbor, depth + 1, new_path))
                return results

            return dfs(start_node_id, 0, [])

    def find_path(self, start_node_id: str, end_node_id: str,
                  max_depth: int = 5, rel_types: list[str] = None) -> Optional[list[dict]]:
        """BFS 查找最短路径"""
        with self._lock:
            if start_node_id not in self._nodes or end_node_id not in self._nodes:
                return None

            visited = {start_node_id}
            queue = [(start_node_id, 0, [])]

            while queue:
                node_id, depth, path = queue.pop(0)
                if node_id == end_node_id:
                    return path

                if depth >= max_depth:
                    continue

                for rel in self._rels.values():
                    if rel.start_node_id != node_id:
                        continue
                    if rel_types and rel.type not in rel_types:
                        continue
                    neighbor = rel.end_node_id
                    if neighbor in visited:
                        continue
                    visited.add(neighbor)
                    new_path = path + [
                        {"type": "node", "data": self._nodes[node_id].to_dict()},
                        {"type": "rel", "data": rel.to_dict()},
                    ]
                    queue.append((neighbor, depth + 1, new_path))

            return None

    def similar_nodes(self, node_id: str, label: str = None, limit: int = 10) -> list[dict]:
        """
        查找相似节点
        策略：通过 SIMILAR_TO 关系 + 共享邻居节点数量计算相似度
        """
        with self._lock:
            if node_id not in self._nodes:
                return []

            # 获取直接相似的节点
            similar_ids = set()
            for rel in self._rels.values():
                if rel.type == RelType.SIMILAR_TO.value:
                    if rel.start_node_id == node_id:
                        similar_ids.add(rel.end_node_id)
                    elif rel.end_node_id == node_id:
                        similar_ids.add(rel.start_node_id)

            # 获取通过共享关系相连的节点（2度关联）
            for rel in self._rels.values():
                if rel.start_node_id == node_id or rel.end_node_id == node_id:
                    other = rel.end_node_id if rel.start_node_id == node_id else rel.start_node_id
                    if other != node_id:
                        similar_ids.add(other)

            results = []
            for nid in similar_ids:
                if nid == node_id:
                    continue
                node = self._nodes[nid]
                if label and node.label != label:
                    continue
                # 计算相似度分数
                score = self._calc_similarity(node_id, nid)
                results.append({"node": node.to_dict(), "score": round(score, 3)})

            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]

    def _calc_similarity(self, node_a: str, node_b: str) -> float:
        """计算两个节点的相似度（基于共享邻居和关系）"""
        # 邻居集合
        neighbors_a = set()
        neighbors_b = set()
        for rel in self._rels.values():
            if rel.start_node_id == node_a:
                neighbors_a.add(rel.end_node_id)
            if rel.end_node_id == node_a:
                neighbors_a.add(rel.start_node_id)
            if rel.start_node_id == node_b:
                neighbors_b.add(rel.end_node_id)
            if rel.end_node_id == node_b:
                neighbors_b.add(rel.start_node_id)

        # Jaccard 相似度
        intersection = len(neighbors_a & neighbors_b)
        union = len(neighbors_a | neighbors_b)
        jaccard = intersection / union if union > 0 else 0

        # 加上直接 SIMILAR_TO 关系权重
        for rel in self._rels.values():
            if rel.type == RelType.SIMILAR_TO.value:
                if (rel.start_node_id == node_a and rel.end_node_id == node_b) or \
                   (rel.start_node_id == node_b and rel.end_node_id == node_a):
                    jaccard += rel.weight * 0.5

        return min(jaccard, 1.0)

    def bulk_import(self, nodes: list[dict], relationships: list[dict]):
        """批量导入节点和关系（用于初始化）"""
        with self._lock:
            for n in nodes:
                node = GraphNode(
                    id=n.get("id", self._gen_id()),
                    label=n["label"],
                    properties=n.get("properties", {}),
                )
                self._nodes[node.id] = node
                self._index_node(node)

            for r in relationships:
                self.create_relationship(
                    start_node_id=r["start_node_id"],
                    end_node_id=r["end_node_id"],
                    rel_type=r["type"],
                    properties=r.get("properties", {}),
                    weight=r.get("weight", 1.0),
                )
            self._persist()

    def _persist(self):
        """持久化到文件"""
        if not self._persist_path:
            return
        import json
        try:
            data = {
                "nodes": [n.to_dict() for n in self._nodes.values()],
                "relationships": [r.to_dict() for r in self._rels.values()],
            }
            with open(self._persist_path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # 持久化失败不影响主功能

    def _load(self):
        """从文件加载"""
        if not self._persist_path:
            return
        import json
        try:
            with open(self._persist_path, "r") as f:
                data = json.load(f)
            for n in data.get("nodes", []):
                node = GraphNode(**n)
                self._nodes[node.id] = node
                self._index_node(node)
            for r in data.get("relationships", []):
                rel = GraphRelationship(**r)
                self._rels[rel.id] = rel
        except Exception:
            pass

    def close(self):
        self._persist()

    def stats(self) -> dict:
        """图谱统计"""
        with self._lock:
            label_counts = {label: len(nodes) for label, nodes in self._node_index.items()}
            rel_type_counts = {}
            for rel in self._rels.values():
                rel_type_counts[rel.type] = rel_type_counts.get(rel.type, 0) + 1
            return {
                "total_nodes": len(self._nodes),
                "total_relationships": len(self._rels),
                "nodes_by_label": label_counts,
                "relationships_by_type": rel_type_counts,
            }


# ─────────────────────────────────────────────────────────────
# Neo4j 驱动（当 Neo4j 服务可用时使用）
# ─────────────────────────────────────────────────────────────

class Neo4jDriver(GraphDBInterface):
    """
    Neo4j 真实连接驱动
    需要: pip install neo4j
    需要: Neo4j 服务运行中（ bolt://localhost:7687 ）
    """

    def __init__(self, uri: str = "bolt://localhost:7687",
                 username: str = "neo4j", password: str = "Admin@123456"):
        try:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(uri, auth=(username, password))
            # 验证连接
            self._driver.verify_connectivity()
            self._use_neo4j = True
        except ImportError:
            raise RuntimeError("neo4j python driver not installed: pip install neo4j")
        except Exception as e:
            raise RuntimeError(f"Cannot connect to Neo4j: {e}")

    def create_node(self, label: str, properties: dict) -> GraphNode:
        node_id = str(uuid.uuid4())[:12]
        properties["_node_id"] = node_id
        with self._driver.session() as session:
            def _create(tx):
                result = tx.run(f"CREATE (n:`{label}` $props) RETURN n", props=properties)
                result.consume()  # consume to commit transaction
            session.execute_write(_create)
        return GraphNode(id=node_id, label=label, properties=properties)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        with self._driver.session() as session:
            result = session.run(
                "MATCH (n) WHERE n._node_id = $id RETURN n",
                id=node_id
            )
            record = result.single()
            if not record:
                return None
            n = record["n"]
            labels = list(n.labels)
            props = dict(n)
            props.pop("_node_id", None)
            return GraphNode(id=node_id, label=labels[0] if labels else "Unknown", properties=props)

    def update_node(self, node_id: str, properties: dict) -> Optional[GraphNode]:
        with self._driver.session() as session:
            def _update(tx):
                tx.run(
                    "MATCH (n) WHERE n._node_id = $id SET n += $props",
                    id=node_id, props=properties
                )
            session.execute_write(_update)
        return self.get_node(node_id)

    def delete_node(self, node_id: str) -> bool:
        with self._driver.session() as session:
            def _delete(tx):
                result = tx.run(
                    "MATCH (n) WHERE n._node_id = $id DETACH DELETE n RETURN count(*)",
                    id=node_id
                )
                record = result.single()
                return record[0] if record else 0
            return session.execute_write(_delete) > 0

    def create_relationship(self, start_node_id: str, end_node_id: str,
                           rel_type: str, properties: dict = None,
                           weight: float = 1.0) -> Optional[GraphRelationship]:
        props = properties or {}
        props["weight"] = weight
        with self._driver.session() as session:
            def _create_rel(tx):
                result = tx.run(
                    f"""
                    MATCH (a), (b)
                    WHERE a._node_id = $start AND b._node_id = $end
                    CREATE (a)-[r:`{rel_type}` $props]->(b)
                    RETURN r
                    """,
                    start=start_node_id, end=end_node_id, props=props
                )
                record = result.single()
                if not record:
                    return None
                rel = record["r"]
                return GraphRelationship(
                    id=str(uuid.uuid4())[:12],
                    start_node_id=start_node_id,
                    end_node_id=end_node_id,
                    type=rel_type,
                    properties=dict(rel),
                    weight=weight,
                )
            return session.execute_write(_create_rel)

    def delete_relationship(self, rel_id: str) -> bool:
        return True  # 简化实现

    def find_nodes(self, label: str, properties: dict = None, limit: int = 100) -> list[GraphNode]:
        with self._driver.session() as session:
            query = f"MATCH (n:`{label}`) RETURN n LIMIT $limit"
            result = session.run(query, limit=limit)
            nodes = []
            for record in result:
                n = record["n"]
                labels = list(n.labels)
                props = dict(n)
                node_id = props.pop("_node_id", str(uuid.uuid4())[:12])
                nodes.append(GraphNode(
                    id=node_id,
                    label=labels[0] if labels else label,
                    properties=props,
                ))
            return nodes

    def find_relationships(self, start_node_id: str = None, end_node_id: str = None,
                          rel_type: str = None) -> list[GraphRelationship]:
        return []

    def traverse_bfs(self, start_node_id: str, max_depth: int = 3,
                     rel_types: list[str] = None) -> list[dict]:
        return []

    def traverse_dfs(self, start_node_id: str, max_depth: int = 3,
                     rel_types: list[str] = None) -> list[dict]:
        return []

    def stats(self) -> dict:
        """图谱统计：节点数和关系数"""
        with self._driver.session() as s1:
            nr = s1.run("MATCH (n) RETURN labels(n)[0] as label, count(*) as cnt")
            node_map = {r["label"]: r["cnt"] for r in nr}
        with self._driver.session() as s2:
            rr = s2.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(*) as cnt")
            rel_map = {r["rel_type"]: r["cnt"] for r in rr}
        return {
            "total_nodes": sum(node_map.values()),
            "total_relationships": sum(rel_map.values()),
            "nodes_by_label": node_map,
            "relationships_by_type": rel_map,
        }

    def find_path(self, start_node_id: str, end_node_id: str,
                  max_depth: int = 5, rel_types: list[str] = None) -> Optional[list[dict]]:
        """查找两点间的所有路径"""
        rel_filter = ""
        if rel_types:
            rel_filter = f"AND type(r) IN {rel_types}"
        query = f"""
            MATCH path = (a) -[r*1..{max_depth}]-> (b)
            WHERE a._node_id = $start AND b._node_id = $end {rel_filter}
            RETURN path, length(path) as hops
            ORDER BY hops ASC LIMIT 10
        """
        with self._driver.session() as session:
            result = session.run(query, start=start_node_id, end=end_node_id)
            paths = []
            for record in result:
                path = record["path"]
                hops = record["hops"]
                nodes = []
                for node in path.nodes:
                    labels = list(node.labels)
                    props = dict(node)
                    props.pop("_node_id", None)
                    nodes.append({
                        "id": props.pop("_node_id", None) or str(uuid.uuid4())[:12],
                        "label": labels[0] if labels else "Unknown",
                        "properties": props,
                    })
                rels = []
                for rel in path.rels:
                    rels.append({
                        "type": type(rel).__name__,
                        "start": rel.start_node._node_id if hasattr(rel.start_node, "_node_id") else None,
                        "end": rel.end_node._node_id if hasattr(rel.end_node, "_node_id") else None,
                        "properties": dict(rel),
                    })
                paths.append({"nodes": nodes, "relationships": rels, "hops": hops})
            return paths if paths else None

    def similar_nodes(self, node_id: str, label: str = None, limit: int = 10) -> list[dict]:
        """查找相似节点（通过 SIMILAR_TO 关系）"""
        label_filter = f"WHERE n:`{label}`" if label else ""
        query = f"""
            MATCH (src) WHERE src._node_id = $node_id
            MATCH (src)-[r:SIMILAR_TO]->(n)
            {label_filter}
            RETURN n, r.score as score, r.reason as reason
            ORDER BY score DESC LIMIT $limit
        """
        with self._driver.session() as session:
            result = session.run(query, node_id=node_id, limit=limit)
            return [
                {
                    "id": dict(r["n"]).pop("_node_id", str(uuid.uuid4())[:12]),
                    "label": list(r["n"].labels)[0] if r["n"].labels else "Unknown",
                    "properties": dict(r["n"]),
                    "score": r["score"],
                    "reason": r["reason"],
                }
                for r in result
            ]

    def close(self):
        if hasattr(self, "_driver"):
            self._driver.close()


# ─────────────────────────────────────────────────────────────
# 全局图数据库实例（根据环境自动选择）
# ─────────────────────────────────────────────────────────────

_graph_db: Optional[GraphDBInterface] = None
_graph_db_lock = threading.Lock()


def get_graph_db(persist_path: str = None) -> GraphDBInterface:
    """
    获取图数据库单例
    优先使用 Neo4j， fallback 到内存图数据库
    """
    global _graph_db
    if _graph_db is not None:
        return _graph_db

    with _graph_db_lock:
        if _graph_db is not None:
            return _graph_db

        # 尝试 Neo4j
        try:
            _graph_db = Neo4jDriver()
            import logging
            logging.getLogger(__name__).warning(f"[GRAPH] Using Neo4jDriver: {_graph_db}")
            return _graph_db
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[GRAPH] Neo4jDriver failed, fallback to InMemoryGraphDB: {e}")

        # Fallback 到内存图数据库
        _graph_db = InMemoryGraphDB(persist_path=persist_path)
        return _graph_db


def reset_graph_db():
    """重置图数据库（用于测试）"""
    global _graph_db
    with _graph_db_lock:
        if _graph_db:
            _graph_db.close()
        _graph_db = None
