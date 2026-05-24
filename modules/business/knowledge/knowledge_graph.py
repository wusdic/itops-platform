"""
知识图谱服务
将故障案例、设备、告警等实体构建为知识图谱
提供图遍历、相似案例推荐、故障传播分析等功能
"""

import logging
from typing import Optional

from modules.business.knowledge.graph_db import (
    get_graph_db, GraphDBInterface, NodeLabel, RelType,
    InMemoryGraphDB
)

logger = logging.getLogger(__name__)

# 持久化路径
GRAPH_PERSIST_PATH = "/home/zcxx/.hermes/projects/itops_platform/data/knowledge_graph.json"


class KnowledgeGraphService:
    """
    知识图谱服务
    封装图数据库操作，提供高层 API
    """

    def __init__(self):
        self._graph: Optional[GraphDBInterface] = None

    @property
    def graph(self) -> GraphDBInterface:
        if self._graph is None:
            self._graph = get_graph_db(persist_path=GRAPH_PERSIST_PATH)
        return self._graph

    def build_graph_from_cases(self, session) -> dict:
        """
        从数据库中的故障案例构建筑识图谱
        节点：故障案例、设备、告警
        关系：案例-设备关联、案例-告警关联、案例-相似案例
        """
        from modules.business.knowledge_base.models import FaultCase
        from modules.foundation.db_models.alert import Alert as AlertModel
        from sqlalchemy import select

        stats = {"nodes_created": 0, "rels_created": 0}

        # 构建设备节点（按 IP 去重）
        devices = session.execute(select(AlertModel.device_ip).distinct().where(
            AlertModel.device_ip.isnot(None)
        )).scalars().all()

        device_nodes = {}
        for ip in devices:
            if ip:
                node = self.graph.create_node(
                    label=NodeLabel.DEVICE.value,
                    properties={"ip": ip, "name": ip}
                )
                device_nodes[ip] = node.id
                stats["nodes_created"] += 1

        # 构建告警节点
        alerts = session.execute(
            select(AlertModel).where(AlertModel.id.isnot(None)).limit(500)
        ).scalars().all()

        alert_nodes = {}
        for alert in alerts:
            node = self.graph.create_node(
                label=NodeLabel.ALERT.value,
                properties={
                    "alert_id": alert.id,
                    "title": alert.title[:100],
                    "level": str(alert.level) if alert.level else "unknown",
                    "device_ip": alert.device_ip,
                }
            )
            alert_nodes[alert.id] = node.id
            stats["nodes_created"] += 1

            # 告警-设备关系
            if alert.device_ip in device_nodes:
                self.graph.create_relationship(
                    start_node_id=node.id,
                    end_node_id=device_nodes[alert.device_ip],
                    rel_type=RelType.AFFECTS.value,
                    weight=0.5,
                )
                stats["rels_created"] += 1

        # 构建故障案例节点
        cases = session.execute(
            select(FaultCase).where(FaultCase.is_deleted == False).limit(500)
        ).scalars().all()

        case_nodes = {}
        for case in cases:
            node = self.graph.create_node(
                label=NodeLabel.FAULT_CASE.value,
                properties={
                    "case_id": case.id,
                    "title": case.title,
                    "fault_level": str(case.fault_level) if case.fault_level else None,
                    "fault_category": case.fault_category,
                    "fault_status": str(case.fault_status) if case.fault_status else None,
                    "symptom": (case.symptom or "")[:500],
                    "root_cause": (case.root_cause or "")[:500],
                    "solution": (case.solution or "")[:500],
                    "prevention": (case.prevention or "")[:500],
                    "tags": case.tags or "",
                    "affected_systems": str(case.affected_systems) if case.affected_systems else None,
                }
            )
            case_nodes[case.id] = node.id
            stats["nodes_created"] += 1

        # 构建案例相似关系（基于故障级别和故障分类）
        for case_a in cases:
            for case_b in cases:
                if case_a.id >= case_b.id:
                    continue
                if case_a.fault_category and case_a.fault_category == case_b.fault_category:
                    # 同类别案例相关
                    score = 0.9 if case_a.fault_level == case_b.fault_level else 0.6
                    self.graph.create_relationship(
                        start_node_id=case_nodes[case_a.id],
                        end_node_id=case_nodes[case_b.id],
                        rel_type=RelType.SIMILAR_TO.value,
                        properties={"score": score, "reason": "same_category"},
                        weight=score,
                    )
                    stats["rels_created"] += 1

        return stats

    def add_case_to_graph(self, case_id: int, properties: dict) -> Optional[dict]:
        """将单个故障案例添加到图谱"""
        # 检查是否已存在
        existing = self.graph.find_nodes(
            label=NodeLabel.FAULT_CASE.value,
            properties={"case_id": case_id}
        )
        if existing:
            return None  # 已存在

        node = self.graph.create_node(
            label=NodeLabel.FAULT_CASE.value,
            properties={
                "case_id": case_id,
                **properties
            }
        )
        return node.to_dict()

    def find_similar_cases(
        self,
        case_id: int,
        max_depth: int = 3,
        limit: int = 10
    ) -> list[dict]:
        """
        查找与指定案例相似的其他案例
        使用图遍历 + 相似度传播算法
        """
        # 找到案例对应的节点 ID
        nodes = self.graph.find_nodes(
            label=NodeLabel.FAULT_CASE.value,
            properties={"case_id": case_id}
        )
        if not nodes:
            return []

        start_node_id = nodes[0].id

        # BFS 遍历找相似节点
        results = self.graph.traverse_bfs(
            start_node_id=start_node_id,
            max_depth=max_depth,
            rel_types=[RelType.SIMILAR_TO.value, RelType.RELATES_TO.value],
        )

        # 收集结果
        similar = []
        seen_ids = set()
        for r in results:
            node_data = r["node"]
            if node_data["properties"].get("case_id") == case_id:
                continue
            nid = node_data["id"]
            if nid in seen_ids:
                continue
            seen_ids.add(nid)

            # 找连接这条关系的权重
            score = 0.5  # 默认分数
            rels = self.graph.find_relationships(
                start_node_id=start_node_id,
                end_node_id=nid,
            )
            for rel in rels:
                if rel.type == RelType.SIMILAR_TO.value:
                    score = max(score, rel.weight)

            similar.append({
                "case_id": node_data["properties"].get("case_id"),
                "title": node_data["properties"].get("title"),
                "fault_level": node_data["properties"].get("fault_level"),
                "symptom": node_data["properties"].get("symptom", "")[:200],
                "root_cause": node_data["properties"].get("root_cause", ""),
                "score": round(score, 2),
                "depth": r["depth"],
            })

        # 按分数排序
        similar.sort(key=lambda x: x["score"], reverse=True)
        return similar[:limit]

    def find_path_between_cases(self, case_a_id: int, case_b_id: int) -> Optional[list[dict]]:
        """查找两个案例之间的关联路径"""
        nodes_a = self.graph.find_nodes(
            label=NodeLabel.FAULT_CASE.value,
            properties={"case_id": case_a_id}
        )
        nodes_b = self.graph.find_nodes(
            label=NodeLabel.FAULT_CASE.value,
            properties={"case_id": case_b_id}
        )
        if not nodes_a or not nodes_b:
            return None

        return self.graph.find_path(
            start_node_id=nodes_a[0].id,
            end_node_id=nodes_b[0].id,
            max_depth=5,
        )

    def get_case_graph_context(
        self,
        case_id: int,
        depth: int = 2
    ) -> dict:
        """
        获取案例的图谱上下文
        包括相似案例、关联设备、关联告警
        """
        nodes = self.graph.find_nodes(
            label=NodeLabel.FAULT_CASE.value,
            properties={"case_id": case_id}
        )
        if not nodes:
            return {"nodes": [], "relationships": [], "stats": self.graph.stats()}

        start_node_id = nodes[0].id

        # 收集所有相关的节点和关系
        visited_nodes = {}
        visited_rels = []

        def collect(node_id: str, current_depth: int):
            if current_depth > depth or node_id in visited_nodes:
                return
            node = self.graph.get_node(node_id)
            if not node:
                return
            visited_nodes[node_id] = node.to_dict()

            for rel in self.graph.find_relationships(start_node_id=node_id):
                if rel.id not in [r["id"] for r in visited_rels]:
                    visited_rels.append(rel.to_dict())
                neighbor = rel.end_node_id if rel.start_node_id == node_id else rel.start_node_id
                collect(neighbor, current_depth + 1)

        collect(start_node_id, 0)

        return {
            "nodes": list(visited_nodes.values()),
            "relationships": visited_rels,
            "stats": self.graph.stats(),
        }

    def stats(self) -> dict:
        """获取图谱统计信息"""
        return self.graph.stats()


# 全局单例
_graph_service: Optional[KnowledgeGraphService] = None


def get_knowledge_graph() -> KnowledgeGraphService:
    global _graph_service
    if _graph_service is None:
        _graph_service = KnowledgeGraphService()
    return _graph_service
