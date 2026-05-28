"""
自动化领域 - Service 层

业务逻辑层，处理自动化脚本和触发规则的核心业务逻辑。
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime


class AutomationService:
    """自动化服务"""

    def __init__(self, db: Session):
        self.db = db

    def list_scripts(self, page=1, page_size=20, name=None, script_type=None) -> Tuple[List, int]:
        """获取自动化脚本列表"""
        from modules.business.automation.models import AutomationScript
        query = self.db.query(AutomationScript)
        if name:
            query = query.filter(AutomationScript.name.like(f"%{name}%"))
        if script_type:
            query = query.filter(AutomationScript.script_type == script_type)
        total = query.count()
        offset = (page - 1) * page_size
        items = query.order_by(AutomationScript.id.desc()).offset(offset).limit(page_size).all()
        return items, total

    def get_script(self, script_id: int) -> Optional[object]:
        from modules.business.automation.models import AutomationScript
        return self.db.query(AutomationScript).filter(AutomationScript.id == script_id).first()

    def create_script(self, req) -> object:
        from modules.business.automation.models import AutomationScript
        script = AutomationScript(
            name=req.name,
            script_type=req.script_type,
            script_content=req.content,
            description=req.description or "",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.db.add(script)
        self.db.commit()
        self.db.refresh(script)
        return script

    def update_script(self, script_id: int, req) -> Optional[object]:
        from modules.business.automation.models import AutomationScript
        script = self.db.query(AutomationScript).filter(AutomationScript.id == script_id).first()
        if not script:
            return None
        if req.name is not None:
            script.name = req.name
        if req.content is not None:
            script.script_content = req.content
        if req.description is not None:
            script.description = req.description
        script.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(script)
        return script

    def delete_script(self, script_id: int) -> bool:
        from modules.business.automation.models import AutomationScript
        script = self.db.query(AutomationScript).filter(AutomationScript.id == script_id).first()
        if not script:
            return False
        self.db.delete(script)
        self.db.commit()
        return True

    def execute_script(self, script_id: int, target: Optional[str] = None) -> dict:
        """执行自动化脚本"""
        script = self.get_script(script_id)
        if not script:
            return {"success": False, "error": "Script not found"}

        # TODO: 调用真正的执行器
        return {
            "success": True,
            "execution_id": f"exec-{script_id}-{datetime.now().timestamp()}",
            "script_name": script.name,
            "target": target,
            "status": "pending",
        }
