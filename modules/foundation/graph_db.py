"""
Neo4j Graph Database Driver for ITOps Platform Knowledge Graph.
Connects to: neo4j://localhost:7687 (Docker neo4j:5.25-community)
Auth: neo4j / Admin@123456
"""
import asyncio
from typing import Any, Optional
from neo4j import AsyncGraphDatabase, Driver, AsyncSession


class Neo4jDriver:
    _instance: Optional["Neo4jDriver"] = None
    _driver: Optional[Driver] = None

    def __init__(self):
        self._uri = "bolt://localhost:7687"
        self._auth = ("neo4j", "Admin@123456")

    @classmethod
    def get_instance(cls) -> "Neo4jDriver":
        if cls._instance is None:
            cls._instance = cls()
        return cls

    def get_driver(self) -> Driver:
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(self._uri, auth=self._auth)
        return self._driver

    async def close(self):
        if self._driver:
            await self._driver.close()
            self._driver = None

    async def _run(
        self, cypher: str, params: Optional[dict] = None
    ) -> list[dict[str, Any]]:
        driver = self.get_driver()
        async with driver.session() as session:
            result = await session.run(cypher, params or {})
            records = await result.data()
            return records

    # ── Schema init ────────────────────────────────────────────────────────────

    async def init_schema(self):
        """Create constraints + indexes if they don't exist."""
        constraints = [
            "CREATE CONSTRAINT device_id IF NOT EXISTS FOR (d:Device) REQUIRE d.device_id IS UNIQUE",
            "CREATE CONSTRAINT alert_id IF NOT EXISTS FOR (a:Alert) REQUIRE a.alert_id IS UNIQUE",
            "CREATE CONSTRAINT wo_id IF NOT EXISTS FOR (w:WorkOrder) REQUIRE w.wo_id IS UNIQUE",
            "CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
        ]
        indexes = [
            "CREATE INDEX device_type IF NOT EXISTS FOR (d:Device) ON (d.device_type)",
            "CREATE INDEX alert_severity IF NOT EXISTS FOR (a:Alert) ON (a.severity)",
            "CREATE INDEX wo_status IF NOT EXISTS FOR (w:WorkOrder) ON (w.status)",
        ]
        for c in constraints + indexes:
            try:
                await self._run(c)
            except Exception:
                pass  # already exists

    # ── Node upserts ────────────────────────────────────────────────────────────

    async def upsert_device(
        self,
        device_id: str,
        name: str,
        device_type: str,
        ip_address: Optional[str] = None,
        status: str = "active",
        **kwargs,
    ) -> str:
        cypher = """
        MERGE (d:Device {device_id: $device_id})
        SET d.name = $name,
            d.device_type = $device_type,
            d.ip_address = $ip_address,
            d.status = $status,
            d.updated_at = datetime()
        WITH d
        CALL apoc.merge.node(
          'Device', {device_id: $device_id},
          {name: $name, device_type: $device_type}, {}
        ) YIELD node
        RETURN node.device_id as id
        """
        try:
            result = await self._run(cypher, {
                "device_id": device_id, "name": name,
                "device_type": device_type, "ip_address": ip_address,
                "status": status,
            })
            return result[0]["id"] if result else device_id
        except Exception:
            # Fallback without apoc
            cypher = """
            MERGE (d:Device {device_id: $device_id})
            SET d.name = $name, d.device_type = $device_type,
                d.ip_address = $ip_address, d.status = $status,
                d.updated_at = datetime()
            RETURN d.device_id as id
            """
            r = await self._run(cyher, {
                "device_id": device_id, "name": name,
                "device_type": device_type, "ip_address": ip_address,
                "status": status,
            })
            return r[0]["id"] if r else device_id

    async def upsert_alert(
        self,
        alert_id: str,
        title: str,
        severity: str,
        device_id: Optional[str] = None,
        status: str = "active",
        **kwargs,
    ) -> str:
        cypher = """
        MERGE (a:Alert {alert_id: $alert_id})
        SET a.title = $title, a.severity = $severity,
            a.device_id = $device_id, a.status = $status,
            a.updated_at = datetime()
        """
        await self._run(cypher, {
            "alert_id": alert_id, "title": title,
            "severity": severity, "device_id": device_id,
            "status": status,
        })
        # Link to device if device_id provided
        if device_id:
            link = """
            MATCH (d:Device {device_id: $device_id})
            MATCH (a:Alert {alert_id: $alert_id})
            MERGE (a)-[:ON_DEVICE]->(d)
            """
            try:
                await self._run(link, {"device_id": device_id, "alert_id": alert_id})
            except Exception:
                pass
        return alert_id

    async def upsert_workorder(
        self,
        wo_id: str,
        title: str,
        status: str,
        priority: str = "medium",
        creator_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        **kwargs,
    ) -> str:
        cypher = """
        MERGE (w:WorkOrder {wo_id: $wo_id})
        SET w.title = $title, w.status = $status,
            w.priority = $priority, w.creator_id = $creator_id,
            w.assignee_id = $assignee_id,
            w.updated_at = datetime()
        """
        await self._run(cypher, {
            "wo_id": wo_id, "title": title,
            "status": status, "priority": priority,
            "creator_id": creator_id, "assignee_id": assignee_id,
        })
        return wo_id

    async def upsert_user(
        self,
        user_id: str,
        username: str,
        role: str = "user",
        **kwargs,
    ) -> str:
        cypher = """
        MERGE (u:User {user_id: $user_id})
        SET u.username = $username, u.role = $role,
            u.updated_at = datetime()
        """
        await self._run(cypher, {
            "user_id": user_id, "username": username, "role": role,
        })
        return user_id

    # ── Relationships ───────────────────────────────────────────────────────────

    async def upsert_relationship(
        self,
        from_id: str,
        to_id: str,
        rel_type: str,
        from_type: str = "Device",
        to_type: str = "Device",
        **properties,
    ) -> bool:
        cypher = f"""
        MATCH (a:{from_type} {{{from_type.lower()}_id: $from_id}})
        MATCH (b:{to_type} {{{to_type.lower()}_id: $to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r = $properties, r.updated_at = datetime()
        """
        try:
            await self._run(cypher, {
                "from_id": from_id, "to_id": to_id,
                "properties": properties,
            })
            return True
        except Exception:
            return False

    # ── Queries ────────────────────────────────────────────────────────────────

    async def query_subgraph(
        self,
        node_type: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get nodes and their relationships."""
        cypher = f"""
        MATCH (n{'::' + node_type if node_type else ''})
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, type(r) as rel_type, m
        LIMIT $limit
        """
        return await self._run(cypher, {"limit": limit})

    async def find_path(
        self,
        from_id: str,
        to_id: str,
        max_hops: int = 3,
    ) -> list[dict]:
        """Find shortest path between two nodes."""
        cypher = """
        MATCH path = (a {device_id: $from_id})
               -[*1..$max_hops]-(b {device_id: $to_id})
        RETURN path, length(path) as hops
        ORDER BY hops ASC LIMIT 1
        """
        return await self._run(cypher, {
            "from_id": from_id, "to_id": to_id,
            "max_hops": max_hops,
        })

    async def get_related_nodes(
        self,
        node_id: str,
        node_type: str = "Device",
        rel_type: Optional[str] = None,
        direction: str = "out",
        limit: int = 50,
    ) -> list[dict]:
        """Get nodes connected to a given node."""
        dir_clause = "-->" if direction == "out" else "<--"
        rel_clause = f"[r:{rel_type}]" if rel_type else "[r]"
        cypher = f"""
        MATCH (n:{node_type} {{{node_type.lower()}_id: $node_id}}})
        OPTIONAL MATCH (n){dir_clause}{rel_clause}(m)
        RETURN m, type(r) as rel_type
        LIMIT $limit
        """
        return await self._run(cypher, {"node_id": node_id, "limit": limit})

    async def stats(self) -> dict:
        """Return node/relationship counts."""
        node_counts = await self._run("""
            MATCH (n) RETURN labels(n)[0] as type, count(*) as count
        """)
        rel_counts = await self._run("""
            MATCH ()-[r]->() RETURN type(r) as type, count(*) as count
        """)
        return {
            "nodes": {r["type"]: r["count"] for r in node_counts},
            "relationships": {r["type"]: r["count"] for r in rel_counts},
        }

    async def clear_all(self) -> bool:
        """DANGER: Clear all nodes and relationships. Use for testing."""
        try:
            await self._run("MATCH (n) DETACH DELETE n")
            return True
        except Exception:
            return False
