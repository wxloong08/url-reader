"""OpenCLI browser-extract fetch strategy."""

import json
import re
import shutil
import subprocess

from scripts.strategies import FetchStrategy


class OpenCLIBrowserStrategy(FetchStrategy):

    name = "OpenCLI Browser"

    def fetch(self, url: str, platform: dict) -> dict:
        opencli_cmd = _resolve_opencli_command()
        if not opencli_cmd:
            return {"success": False, "error": "opencli 未安装"}

        tab_id = ""
        try:
            opened = self._run_json([opencli_cmd, "browser", "open", url])
            tab_id = str(opened.get("page", "")).strip()
            if not tab_id:
                return {"success": False, "error": "opencli 未返回页面标识"}

            extract = self._extract_tab(opencli_cmd, tab_id)
            content = str(extract.get("content", "")).strip()
            if not content:
                return {"success": False, "error": "opencli 提取内容过短"}

            return {
                "success": True,
                "strategy": self.name,
                "content": content,
                "metadata": {
                    "title": str(extract.get("title", "")).strip(),
                    "source_url": str(extract.get("url", url)).strip() or url,
                },
            }
        except Exception as e:
            return {"success": False, "error": f"OpenCLI Browser 错误: {e}"}
        finally:
            if tab_id:
                try:
                    subprocess.run(
                        [opencli_cmd, "browser", "tab", "close", tab_id],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        check=False,
                    )
                except Exception:
                    pass

    def _extract_tab(self, opencli_cmd: str, tab_id: str) -> dict:
        try:
            return self._run_json([opencli_cmd, "browser", "extract", "--tab", tab_id, "--selector", "main"])
        except RuntimeError as exc:
            if "selector_not_found" not in str(exc):
                raise
        return self._run_json([opencli_cmd, "browser", "extract", "--tab", tab_id])

    @staticmethod
    def _run_json(command: list[str]) -> dict:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        stdout = (completed.stdout or "").strip()
        stderr = (completed.stderr or "").strip()

        payload_text = stdout or stderr
        payload = _parse_json_payload(payload_text)
        if completed.returncode == 0:
            if isinstance(payload, dict):
                return payload
            raise RuntimeError("命令返回结果不是 JSON 对象")

        if isinstance(payload, dict):
            error_info = payload.get("error")
            if isinstance(error_info, dict):
                code = error_info.get("code")
                message = error_info.get("message")
                if code and message:
                    raise RuntimeError(f"{code}: {message}")
                if message:
                    raise RuntimeError(str(message))
            if payload.get("message"):
                raise RuntimeError(str(payload["message"]))

        raise RuntimeError(stderr or stdout or f"命令失败: {' '.join(command)}")


def _parse_json_payload(text: str):
    text = text.strip()
    if not text:
        return {}

    for opener, closer in (("{", "}"), ("[", "]")):
        start = text.find(opener)
        end = text.rfind(closer)
        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

    # Fallback for trailing notice lines after a valid first JSON line.
    first_line = text.splitlines()[0].strip()
    if first_line:
        return json.loads(first_line)
    return {}


def _resolve_opencli_command() -> str:
    for candidate in ("opencli.cmd", "opencli", "opencli.ps1"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    return ""
