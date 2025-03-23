from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import logging
from typing import Dict

from module.utils import LOG_ROOT


class OpenAILogger:
    def __init__(self):
        self.log_root = LOG_ROOT
        self.handlers: Dict[str, logging.FileHandler] = {}  # 缓存 Handler

        # 创建根 Logger
        self.logger = logging.getLogger("conversation_logger")
        self.logger.setLevel(logging.INFO)

    def add_handler(self, ui_page: str, session_ts: str, log_dir) -> str:
        """为当前主界面会话添加 Handler"""
        handler_key = f"{ui_page}_{session_ts}"

        if handler_key not in self.handlers:
            # 创建 Handler
            log_file = f"{log_dir}/conversations.log"
            handler = logging.FileHandler(log_file, encoding="utf-8")
            formatter = logging.Formatter(
                "%(asctime)s - [task: %(task)s] - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)

            # 缓存并添加到 Logger
            self.handlers[handler_key] = handler
            self.logger.addHandler(handler)

        return handler_key

    def log(
            self,
            ui_page: str,
            task: str,
            messages: list,
            full_response: str
    ):
        """记录日志"""
        # 格式化日志内容
        messages_str = "\n".join([f"[{msg['role']}] {msg['content']}" for msg in messages])
        log_content = (
            f"Conversation Start.\n"
            f"{'-' * 50}\nMESSAGE:\n{messages_str}\n"
            f"{'-' * 50}\nRESPONSE:\n{full_response}\n"
            f"{'-' * 50}\nConversation End.\n{'=' * 50}"
        )

        # 记录日志
        self.logger.info(
            log_content,
            extra={"task": f"{ui_page}.{task}"}
        )

    def cleanup(self, ui_page: str, session_ts: str):
        """清理指定 Handler"""
        handler_key = f"{ui_page}_{session_ts}"
        if handler_key in self.handlers:
            handler = self.handlers.pop(handler_key)
            self.logger.removeHandler(handler)
            handler.close()
