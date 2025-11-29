import threading
from pynput import keyboard

from game_automator.workflows import discover_workflows


class HotkeyListener:
    """Listens for global hotkeys to trigger workflows."""
    
    def __init__(self):
        self.workflows = discover_workflows()
        self.running = False
        self.current_workflow = None
        self.listener = None
    
    def start(self):
        """Start listening for hotkeys."""
        print("Hotkey listener started!")
        print("  F9  = Run city-investment-scan")
        print("  F10 = Stop current workflow")
        print("  F12 = Exit")
        print()
        print("Waiting for hotkey...")
        
        self.running = True
        
        with keyboard.Listener(on_press=self.on_press) as listener:
            self.listener = listener
            listener.join()
    
    def on_press(self, key):
        try:
            if key == keyboard.Key.f9:
                self.run_workflow("city-investment-scan")
            elif key == keyboard.Key.f10:
                print("\n[HOTKEY] Stop requested (not implemented yet)")
            elif key == keyboard.Key.f12:
                print("\n[HOTKEY] Exiting...")
                return False  # Stop listener
        except Exception as e:
            print(f"[ERROR] Hotkey error: {e}")
    
    def run_workflow(self, name: str):
        if name not in self.workflows:
            print(f"[ERROR] Unknown workflow: {name}")
            return
        
        print(f"\n[HOTKEY] Starting workflow: {name}")
        
        # Run workflow in a separate thread so hotkeys still work
        def run():
            workflow_class = self.workflows[name]
            workflow = workflow_class()
            workflow.execute()
            print("\nWaiting for hotkey...")
        
        thread = threading.Thread(target=run)
        thread.start()


def main():
    listener = HotkeyListener()
    listener.start()


if __name__ == "__main__":
    main()