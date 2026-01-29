import subprocess
import webbrowser
import psutil
import platform
import os
from typing import Dict, Any, List
from datetime import datetime
import logging
import urllib.parse

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    logging.warning("pyautogui not available - screenshot functionality disabled")

logger = logging.getLogger(__name__)

class WorkflowExecutor:
    def __init__(self):
        self.active_tasks = []
        self.os_type = platform.system()
        self.is_wsl = "microsoft" in platform.uname().release.lower()
        
        self.app_commands = {
            "chrome": self._get_browser_command("chrome"),
            "firefox": self._get_browser_command("firefox"),
            "edge": self._get_browser_command("edge"),
            "vscode": self._get_app_command("code"),
            "terminal": self._get_terminal_command(),
            "notepad": self._get_app_command("notepad"),
            "calculator": self._get_app_command("calc"),
        }
    
    def _open_url_wsl(self, url: str) -> bool:
        try:
            subprocess.run(
                ["cmd.exe", "/c", "start", url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
            return True
        except Exception as e:
            logger.error(f"WSL browser open failed: {e}")
            return False
    
    def _get_browser_command(self, browser: str) -> str:
        if self.os_type == "Windows":
            browsers = {
                "chrome": "chrome",
                "firefox": "firefox",
                "edge": "msedge"
            }
            return browsers.get(browser, browser)
        elif self.os_type == "Linux":
            is_wsl = "microsoft" in platform.uname().release.lower()
            if is_wsl:
                browsers = {
                    "chrome": "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
                    "firefox": "/mnt/c/Program Files/Mozilla Firefox/firefox.exe",
                    "edge": "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
                }
            else:
                browsers = {
                    "chrome": "google-chrome",
                    "firefox": "firefox",
                    "edge": "microsoft-edge"
                }
            return browsers.get(browser, browser)
        else:
            return browser
    
    def _get_app_command(self, app: str) -> str:
        if self.os_type == "Windows":
            return app
        elif self.os_type == "Linux":
            return app.lower()
        return app
    
    def _get_terminal_command(self) -> str:
        if self.os_type == "Windows":
            return "cmd"
        elif self.os_type == "Linux":
            return "gnome-terminal"
        else:
            return "terminal"
    
    async def execute(self, intent_data: Dict[str, Any]) -> Dict[str, Any]:
        intent = intent_data.get("intent", "unknown")
        entities = intent_data.get("entities", {})
        
        handlers = {
            "open_application": self._open_application,
            "close_application": self._close_application,
            "web_search": self._web_search,
            "open_website": self._open_website,
            "file_operation": self._file_operation,
            "system_control": self._system_control,
            "time_date": self._time_date,
            "information": self._information,
            "conversation": self._conversation,
        }
        
        handler = handlers.get(intent, self._unknown_intent)
        
        try:
            result = await handler(entities, intent_data)
            return result
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                "success": False,
                "message": f"Failed to execute command: {str(e)}"
            }
    
    async def _open_application(self, entities: Dict, intent_data: Dict) -> Dict[str, Any]:
        app_name = entities.get("target", "").lower()
        
        if not app_name:
            return {"success": False, "message": "No application specified"}
        
        command = self.app_commands.get(app_name)
        
        if not command:
            command = app_name
        
        try:
            is_wsl = "microsoft" in platform.uname().release.lower()
            
            if is_wsl:
                if command.endswith(".exe"):
                    if not os.path.exists(command):
                        alt_paths = [
                            f"/mnt/c/Program Files/{app_name.capitalize()}/{app_name}.exe",
                            f"/mnt/c/Program Files (x86)/{app_name.capitalize()}/{app_name}.exe"
                        ]
                        for alt_path in alt_paths:
                            if os.path.exists(alt_path):
                                command = alt_path
                                break
                    
                    subprocess.Popen([command], shell=False, 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen(["cmd.exe", "/c", "start", app_name], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
            elif self.os_type == "Windows":
                subprocess.Popen(command, shell=True)
            else:
                subprocess.Popen([command])
            
            app_responses = {
                "chrome": "Opening Chrome for you",
                "firefox": "Launching Firefox",
                "edge": "Starting Edge",
                "vscode": "Opening VS Code",
                "terminal": "Opening terminal",
            }
            message = app_responses.get(app_name, f"Opening {app_name}")
            return {
                "success": True,
                "message": message
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Could not open {app_name}: {str(e)}"
            }
    
    async def _close_application(self, entities: Dict, intent_data: Dict) -> Dict[str, Any]:
        app_name = entities.get("target", "").lower()
        
        if not app_name:
            return {"success": False, "message": "No application specified"}
        
        try:
            for proc in psutil.process_iter(['name']):
                if app_name in proc.info['name'].lower():
                    proc.terminate()
                    return {
                        "success": True,
                        "message": f"Closed {app_name}"
                    }
            
            return {
                "success": False,
                "message": f"{app_name} is not running"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Could not close {app_name}: {str(e)}"
            }
    
    async def _web_search(self, entities: Dict, intent_data: Dict) -> Dict[str, Any]:
        query = entities.get("target", "")
        
        if not query:
            return {"success": False, "message": "No search query provided"}
        
        query = query.strip()
        
        special_searches = {
            "youtube": "https://www.youtube.com/results?search_query=",
            "reddit": "https://www.reddit.com/search/?q=",
            "github": "https://github.com/search?q="
        }
        
        search_on = None
        for site, base_url in special_searches.items():
            if f"on {site}" in query.lower() or f"{site} for" in query.lower():
                search_on = site
                query = query.lower().replace(f"on {site}", "").replace(f"{site} for", "").strip()
                break
        
        if search_on:
            search_url = special_searches[search_on] + query.replace(' ', '+')
        else:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        try:
            if self.is_wsl:
                success = self._open_url_wsl(search_url)
            else:
                webbrowser.open(search_url)
                success = True
            
            if success:
                return {
                    "success": True,
                    "message": f"Here's what I found for {query}"
                }
            else:
                return {
                    "success": False,
                    "message": f"Search failed"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Search failed: {str(e)}"
            }
    
    async def _open_website(self, entities: Dict, intent_data: Dict) -> Dict[str, Any]:
        url = entities.get("target", "")
        original_text = intent_data.get("original_text", "").lower()
        
        if "new tab" in original_text or "open tab" in original_text or not url:
            url = "about:blank"
        
        url = url.strip().lower()
        
        common_sites = {
            "youtube": "https://www.youtube.com",
            "gmail": "https://mail.google.com",
            "github": "https://github.com",
            "reddit": "https://reddit.com",
            "twitter": "https://twitter.com",
            "facebook": "https://facebook.com",
            "linkedin": "https://linkedin.com",
            "instagram": "https://instagram.com",
            "netflix": "https://netflix.com",
            "amazon": "https://amazon.com",
            "google": "https://www.google.com",
            "wikipedia": "https://www.wikipedia.org",
            "stackoverflow": "https://stackoverflow.com",
            "medium": "https://medium.com",
            "twitch": "https://www.twitch.tv",
            "discord": "https://discord.com",
            "spotify": "https://open.spotify.com"
        }
        
        if url in common_sites:
            url = common_sites[url]
        elif not url.startswith(("http://", "https://")):
            if "." not in url:
                url = f"https://www.{url}.com"
            else:
                url = "https://" + url
        
        try:
            if self.is_wsl:
                success = self._open_url_wsl(url)
            else:
                webbrowser.open(url)
                success = True
            
            if success:
                site_name = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
                return {
                    "success": True,
                    "message": f"Opening {site_name}"
                }
            else:
                return {
                    "success": False,
                    "message": f"Could not open {url}"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Could not open {url}: {str(e)}"
            }
    
    async def _file_operation(self, entities: Dict, intent_data: Dict) -> Dict[str, Any]:
        operation = intent_data.get("original_text", "").lower()
        target = entities.get("target", "")
        
        if "create" in operation:
            try:
                with open(target, 'w') as f:
                    f.write("")
                return {
                    "success": True,
                    "message": f"Created file {target}"
                }
            except Exception as e:
                return {"success": False, "message": str(e)}
        
        elif "delete" in operation:
            try:
                os.remove(target)
                return {
                    "success": True,
                    "message": f"Deleted file {target}"
                }
            except Exception as e:
                return {"success": False, "message": str(e)}
        
        elif "open" in operation:
            try:
                if self.os_type == "Windows":
                    os.startfile(target)
                else:
                    subprocess.Popen(["xdg-open", target])
                return {
                    "success": True,
                    "message": f"Opening file {target}"
                }
            except Exception as e:
                return {"success": False, "message": str(e)}
        
        return {"success": False, "message": "Unknown file operation"}
    
    async def _system_control(self, entities: Dict, intent_data: Dict) -> Dict[str, Any]:
        command = intent_data.get("original_text", "").lower()
        
        if "screenshot" in command:
            if not PYAUTOGUI_AVAILABLE:
                return {
                    "success": False,
                    "message": "Screenshot functionality requires pyautogui (pip install pyautogui)"
                }
            try:
                screenshot = pyautogui.screenshot()
                filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot.save(filename)
                return {
                    "success": True,
                    "message": f"Screenshot saved as {filename}"
                }
            except Exception as e:
                return {"success": False, "message": str(e)}
        
        elif "volume" in command:
            action = entities.get("target", "")
            return {
                "success": True,
                "message": f"Volume {action} (system integration required)"
            }
        
        elif "brightness" in command:
            level = entities.get("target", "")
            return {
                "success": True,
                "message": f"Brightness set to {level} (system integration required)"
            }
        
        return {"success": False, "message": "Unknown system control command"}
    
    async def _time_date(self, entities: Dict, intent_data: Dict) -> Dict[str, Any]:
        command = intent_data.get("original_text", "").lower()
        
        if "time" in command:
            current_time = datetime.now().strftime("%I:%M %p")
            return {
                "success": True,
                "message": f"The time is {current_time}"
            }
        
        elif "date" in command or "day" in command:
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            return {
                "success": True,
                "message": f"Today is {current_date}"
            }
        
        return {"success": False, "message": "Unknown time/date query"}
    
    async def _information(self, entities: Dict, intent_data: Dict) -> Dict[str, Any]:
        query = entities.get("target", "")
        original = intent_data.get("original_text", "").lower()
        
        responses = {
            "your name": "I'm JARVIS, your personal assistant. I'm here to help with searches, opening apps, and managing your workflow.",
            "who are you": "I'm JARVIS. Think of me as your digital companion who's here to make your life easier.",
            "how are you": "I'm doing great, thanks! What can I help you with?",
            "what can you do": "I can open apps, search the web, tell you the time, open websites, and automate tasks. Try saying 'open YouTube' or 'search for AI news'!",
            "help": "I'm here to help! Just ask me to open apps like Chrome, search the web, open websites like YouTube, or check the time. What would you like to try?",
            "thank you": "You're welcome! Anytime you need me, just ask.",
            "thanks": "My pleasure! I'm always here if you need anything."
        }
        
        for key, response in responses.items():
            if key in original:
                return {
                    "success": True,
                    "message": response
                }
        
        if query:
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            if self.is_wsl:
                self._open_url_wsl(search_url)
            else:
                webbrowser.open(search_url)
            return {
                "success": True,
                "message": f"Let me look that up for you"
            }
        
        return {
            "success": True,
            "message": "I'm listening! Just ask me to open apps, search the web, or check the time."
        }
    
    async def _conversation(self, entities: Dict, intent_data: Dict) -> Dict[str, Any]:
        query = entities.get("query", "")
        return {
            "success": True,
            "message": "Let me think about that...",
            "data": {"needs_ai": True}
        }
    
    async def _unknown_intent(self, entities: Dict, intent_data: Dict) -> Dict[str, Any]:
        original = intent_data.get("original_text", "")
        return {
            "success": False,
            "message": f"I'm not sure what you mean by '{original}'. Try asking me to open Chrome, search for something, or check the time."
        }
    
    def get_active_tasks(self) -> List[str]:
        return self.active_tasks
