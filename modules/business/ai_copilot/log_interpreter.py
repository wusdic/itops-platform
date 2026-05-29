"""
BM-05 AI Copilot - Log Interpreter
AI日志解释模块

解析日志内容，识别日志模式（正常/警告/错误/严重），推断问题根因，
并生成可操作的建议。
"""

import logging
import json
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class LogPattern:
    """日志模式"""
    pattern_type: str  # normal, warning, error, critical
    pattern_name: str
    description: str
    matched_lines: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class LogInterpretationResult:
    """日志解释结果"""
    success: bool
    # 日志概述
    summary: str = ""
    # 日志条数统计
    total_lines: int = 0
    line_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    debug_count: int = 0
    # 识别到的模式
    patterns: List[LogPattern] = field(default_factory=list)
    # 推断的问题根因
    inferred_problems: List[Dict] = field(default_factory=list)
    # 建议的行动
    recommended_actions: List[str] = field(default_factory=list)
    # 时间范围
    time_range_start: str = ""
    time_range_end: str = ""
    # 关键字统计
    top_keywords: List[Dict] = field(default_factory=list)
    # 错误详情
    error_details: List[Dict] = field(default_factory=list)
    # LLM解释（如有）
    llm_explanation: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_msg: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "summary": self.summary,
            "total_lines": self.total_lines,
            "line_count": self.line_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "debug_count": self.debug_count,
            "patterns": [
                {
                    "pattern_type": p.pattern_type,
                    "pattern_name": p.pattern_name,
                    "description": p.description,
                    "matched_lines": p.matched_lines[:10],  # 最多返回10条
                    "confidence": p.confidence,
                }
                for p in self.patterns
            ],
            "inferred_problems": self.inferred_problems,
            "recommended_actions": self.recommended_actions,
            "time_range_start": self.time_range_start,
            "time_range_end": self.time_range_end,
            "top_keywords": self.top_keywords,
            "error_details": self.error_details[:20],  # 最多返回20条
            "llm_explanation": self.llm_explanation,
            "metadata": self.metadata,
            "error_msg": self.error_msg,
        }


class LogInterpreter:
    """
    AI日志解释器

    支持:
    - 基于规则的模式识别（无需LLM）
    - 基于LLM的深度解释（可选）
    - 关键字统计和排序
    - 错误聚合和分类
    """

    # 日志级别关键词
    LOG_LEVEL_KEYWORDS = {
        "error": ["ERROR", "FATAL", "CRITICAL", "Exception", "exception", "Err:", "error:", "FAILED", "failed"],
        "warning": ["WARN", "WARNING", "warn:", "WARNING:", "Degraded", "degraded"],
        "info": ["INFO", "info:", "Info:", "NOTICE"],
        "debug": ["DEBUG", "debug:", "DEBUG:", "TRACE", "trace:"],
    }

    # 常见错误模式
    ERROR_PATTERNS = {
        "connection_refused": {
            "keywords": ["Connection refused", "ECONNREFUSED", "connection refused", "无法连接"],
            "severity": "critical",
            "description": "远程服务拒绝连接",
            "actions": ["检查目标服务是否运行", "检查网络连通性", "检查端口是否开放", "检查防火墙规则"]
        },
        "timeout": {
            "keywords": ["timeout", "TIMEOUT", "timed out", "连接超时", "请求超时"],
            "severity": "error",
            "description": "操作超时",
            "actions": ["检查网络延迟", "增加超时时间", "检查目标服务负载", "查看是否有网络抖动"]
        },
        "out_of_memory": {
            "keywords": ["OutOfMemory", "out of memory", "OOM", "内存不足", "memory error"],
            "severity": "critical",
            "description": "内存不足",
            "actions": ["检查进程内存使用", "增加可用内存", "分析内存泄漏", "优化内存占用"]
        },
        "disk_full": {
            "keywords": ["No space left", "disk full", "no space left on device", "磁盘已满"],
            "severity": "critical",
            "description": "磁盘空间不足",
            "actions": ["清理磁盘空间", "删除旧日志", "扩展磁盘容量", "检查大文件"]
        },
        "permission_denied": {
            "keywords": ["Permission denied", "权限不足", "access denied", "EACCES"],
            "severity": "error",
            "description": "权限拒绝",
            "actions": ["检查文件权限", "检查SELinux/AppArmor", "使用sudo运行"]
        },
        "file_not_found": {
            "keywords": ["File not found", "No such file", "文件不存在", "ENOENT"],
            "severity": "error",
            "description": "文件不存在",
            "actions": ["检查文件路径", "检查文件是否被删除", "检查配置文件路径"]
        },
        "process_not_found": {
            "keywords": ["Process not found", "no such process", "进程不存在", "PID not found"],
            "severity": "warning",
            "description": "进程不存在",
            "actions": ["检查进程是否运行", "检查PID是否正确", "查看进程列表"]
        },
        "service_unavailable": {
            "keywords": ["Service Unavailable", "503", "Service unavailable", "服务不可用"],
            "severity": "error",
            "description": "服务不可用",
            "actions": ["检查服务状态", "检查服务依赖", "查看服务健康检查", "检查上游服务"]
        },
        "authentication_failed": {
            "keywords": ["Authentication failed", "auth failed", "认证失败", "login failed", "401 Unauthorized"],
            "severity": "error",
            "description": "认证失败",
            "actions": ["检查用户名密码", "检查Token是否过期", "检查认证服务"]
        },
        "database_error": {
            "keywords": ["MySQL", "PostgreSQL", "database error", "DB error", "SQL error", "连接数据库失败", "Lost connection"],
            "severity": "critical",
            "description": "数据库错误",
            "actions": ["检查数据库连接", "检查数据库服务状态", "查看数据库日志", "检查连接池配置"]
        },
        "syntax_error": {
            "keywords": ["SyntaxError", "syntax error", "语法错误", "Parse error", "解析错误"],
            "severity": "error",
            "description": "语法错误",
            "actions": ["检查代码语法", "查看具体报错行", "检查环境版本"]
        },
        "api_error": {
            "keywords": ["API error", "HTTP 500", "HTTP 502", "HTTP 504", "api error"],
            "severity": "error",
            "description": "API调用错误",
            "actions": ["检查API服务状态", "查看具体错误信息", "检查请求参数", "检查API配额"]
        },
    }

    def __init__(self):
        """初始化日志解释器"""
        self.llm_client = None
        self._pattern_cache: Dict[str, re.Pattern] = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """预编译正则表达式"""
        for name, pattern_def in self.ERROR_PATTERNS.items():
            for kw in pattern_def["keywords"]:
                try:
                    self._pattern_cache[kw.lower()] = re.compile(re.escape(kw), re.IGNORECASE)
                except re.error:
                    pass

    def set_llm_client(self, llm_client):
        """设置LLM客户端"""
        self.llm_client = llm_client

    def interpret(
        self,
        logs: List[Dict[str, Any]],
        use_llm: bool = False,
        max_lines: int = 500,
    ) -> LogInterpretationResult:
        """
        解释日志内容

        Args:
            logs: 日志列表，每项包含 content, timestamp, stream 等字段
            use_llm: 是否使用LLM深度解释
            max_lines: 最大处理行数

        Returns:
            LogInterpretationResult 解释结果
        """
        if not logs:
            return LogInterpretationResult(
                success=False,
                error_msg="日志列表为空"
            )

        # 限制处理行数
        logs = logs[:max_lines]
        total_lines = len(logs)

        # 统计各级别日志数量
        level_counts = {"error": 0, "warning": 0, "info": 0, "debug": 0, "unknown": 0}
        pattern_matches: Dict[str, List[str]] = {}
        error_details: List[Dict] = []
        keywords_freq: Dict[str, int] = {}
        timestamps: List[str] = []

        for log in logs:
            content = str(log.get("content", ""))
            timestamp = log.get("timestamp", "")

            if timestamp:
                timestamps.append(str(timestamp))

            # 检测日志级别
            level = self._detect_level(content)
            level_counts[level] = level_counts.get(level, 0) + 1

            # 匹配错误模式
            for pattern_name, pattern_def in self.ERROR_PATTERNS.items():
                for kw in pattern_def["keywords"]:
                    if kw.lower() in content.lower():
                        if pattern_name not in pattern_matches:
                            pattern_matches[pattern_name] = []
                        if content not in pattern_matches[pattern_name]:
                            pattern_matches[pattern_name].append(content)
                        break

            # 提取关键字（简单词频统计，排除常见词）
            words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_-]{2,}\b', content.lower())
            stopwords = {"the", "and", "for", "are", "but", "not", "you", "all", "can", "was", "has", "have", "had", "will", "with", "from", "this", "that", "into", "than", "them", "then", "when", "where", "which", "what", "how", "info", "debug", "error", "warn", "warning", "line", "file", "module", "function"}
            for word in words:
                if word not in stopwords and len(word) > 3:
                    keywords_freq[word] = keywords_freq.get(word, 0) + 1

            # 收集错误详情
            if level in ("error", "critical"):
                error_details.append({
                    "content": content[:200],
                    "timestamp": timestamp,
                    "stream": log.get("stream", "unknown"),
                })

        # 构建模式列表
        patterns: List[LogPattern] = []
        for pattern_name, matched_lines in pattern_matches.items():
            pattern_def = self.ERROR_PATTERNS.get(pattern_name, {})
            patterns.append(LogPattern(
                pattern_type=pattern_def.get("severity", "error"),
                pattern_name=pattern_name,
                description=pattern_def.get("description", pattern_name),
                matched_lines=matched_lines[:5],
                confidence=min(1.0, len(matched_lines) / 5),
            ))

        # 推断问题
        inferred_problems = self._infer_problems(pattern_matches, level_counts)

        # 生成建议
        recommended_actions = self._generate_actions(pattern_matches, inferred_problems)

        # Top关键字
        top_keywords = sorted(keywords_freq.items(), key=lambda x: x[1], reverse=True)[:15]
        top_keywords = [{"keyword": k, "count": c} for k, c in top_keywords]

        # 时间范围
        time_start = timestamps[0] if timestamps else ""
        time_end = timestamps[-1] if timestamps else ""

        result = LogInterpretationResult(
            success=True,
            summary=self._generate_summary(level_counts, patterns, inferred_problems),
            total_lines=total_lines,
            line_count=total_lines,
            error_count=level_counts.get("error", 0) + level_counts.get("critical", 0),
            warning_count=level_counts.get("warning", 0),
            info_count=level_counts.get("info", 0),
            debug_count=level_counts.get("debug", 0),
            patterns=patterns,
            inferred_problems=inferred_problems,
            recommended_actions=recommended_actions,
            time_range_start=time_start,
            time_range_end=time_end,
            top_keywords=top_keywords,
            error_details=error_details,
            metadata={
                "processed_at": datetime.now().isoformat(),
                "use_llm": use_llm,
                "max_lines": max_lines,
            },
        )

        # LLM深度解释
        if use_llm and self.llm_client:
            try:
                result.llm_explanation = self._call_llm_explain(logs, result)
            except Exception as e:
                logger.warning(f"LLM解释失败: {e}")
                result.llm_explanation = f"[LLM解释暂时不可用: {str(e)}]"

        return result

    def _detect_level(self, content: str) -> str:
        """检测日志级别"""
        content_lower = content.lower()
        for level, keywords in self.LOG_LEVEL_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in content_lower:
                    return level
        return "unknown"

    def _infer_problems(
        self,
        pattern_matches: Dict[str, List[str]],
        level_counts: Dict[str, int]
    ) -> List[Dict]:
        """根据模式匹配推断问题"""
        problems = []
        error_total = level_counts.get("error", 0) + level_counts.get("critical", 0)

        for pattern_name, matched_lines in pattern_matches.items():
            pattern_def = self.ERROR_PATTERNS.get(pattern_name, {})
            problems.append({
                "problem_type": pattern_name,
                "description": pattern_def.get("description", pattern_name),
                "severity": pattern_def.get("severity", "error"),
                "occurrence_count": len(matched_lines),
                "sample_error": matched_lines[0][:200] if matched_lines else "",
                "actions": pattern_def.get("actions", []),
            })

        # 按严重程度排序
        severity_order = {"critical": 0, "error": 1, "warning": 2}
        problems.sort(key=lambda x: severity_order.get(x["severity"], 3))

        # 如果有大量错误但没有匹配到已知模式，添加通用问题
        if error_total > 10 and len(problems) == 0:
            problems.append({
                "problem_type": "unknown_high_error_rate",
                "description": f"高错误率：共 {error_total} 条错误日志",
                "severity": "error",
                "occurrence_count": error_total,
                "sample_error": "",
                "actions": ["检查所有错误日志详情", "查看错误时间分布", "检查最近变更"]
            })

        return problems

    def _generate_actions(
        self,
        pattern_matches: Dict[str, List[str]],
        inferred_problems: List[Dict]
    ) -> List[str]:
        """生成推荐行动"""
        all_actions: Dict[str, int] = {}
        for problem in inferred_problems:
            for action in problem.get("actions", []):
                all_actions[action] = all_actions.get(action, 0) + 1

        # 按出现频率排序
        sorted_actions = sorted(all_actions.items(), key=lambda x: x[1], reverse=True)
        return [action for action, _ in sorted_actions[:8]]

    def _generate_summary(
        self,
        level_counts: Dict[str, int],
        patterns: List[LogPattern],
        inferred_problems: List[Dict]
    ) -> str:
        """生成日志摘要"""
        total = sum(level_counts.values())
        error_total = level_counts.get("error", 0) + level_counts.get("critical", 0)
        warning_total = level_counts.get("warning", 0)

        if error_total == 0 and warning_total == 0:
            return f"日志正常，共 {total} 条记录，无错误或警告。"
        elif error_total > 0 and len(patterns) > 0:
            top_problem = patterns[0]
            return f"发现 {error_total} 条错误日志，主要问题：{top_problem.description}。"
        elif warning_total > 0:
            return f"共 {total} 条日志，其中 {warning_total} 条警告，{error_total} 条错误。"
        else:
            return f"共 {total} 条日志，其中 {error_total} 条错误。"

    def _call_llm_explain(
        self,
        logs: List[Dict[str, Any]],
        result: LogInterpretationResult
    ) -> str:
        """调用LLM进行深度解释"""
        if not self.llm_client:
            return ""

        # 构建提示
        log_sample = "\n".join([
            f"[{log.get('timestamp', 'N/A')}] {str(log.get('content', ''))[:200]}"
            for log in logs[:50]
        ])

        prompt = f"""你是一位运维工程师。请分析以下日志内容，并给出简洁的解释和建议。

## 日志统计
{result.summary}
错误数：{result.error_count}，警告数：{result.warning_count}，总行数：{result.line_count}

## 识别到的问题
{json.dumps(result.inferred_problems[:3], ensure_ascii=False, indent=2)}

## 日志样例（按时间顺序）
{log_sample}

请用50字以内解释这些日志表明了什么问题，并给出最重要的2-3条处理建议。用中文回答。
"""

        try:
            response = self.llm_client.chat([
                {"role": "user", "content": prompt}
            ])
            return response.get("content", response.get("message", {}).get("content", ""))
        except Exception as e:
            logger.warning(f"LLM调用失败: {e}")
            return ""


# 全局单例
_log_interpreter: Optional[LogInterpreter] = None


def get_log_interpreter() -> LogInterpreter:
    """获取全局LogInterpreter单例"""
    global _log_interpreter
    if _log_interpreter is None:
        _log_interpreter = LogInterpreter()
    return _log_interpreter


def init_log_interpreter(llm_client=None) -> LogInterpreter:
    """初始化LogInterpreter"""
    global _log_interpreter
    _log_interpreter = LogInterpreter()
    if llm_client:
        _log_interpreter.set_llm_client(llm_client)
    return _log_interpreter
