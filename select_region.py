"""
Run this once to pick two regions:
  1. TRIGGER region  - the small area to watch (e.g. just the "unavailable" text)
  2. CAPTURE region   - the larger area to screenshot once the trigger changes

For each, click and drag a box, then release. You'll be prompted twice.
Writes both to region.json.
"""
import tkinter as tk
import json


class RegionSelector:
    def __init__(self, prompt_text):
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.3)
        self.root.configure(bg="black")
        self.root.attributes("-topmost", True)

        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey11")
        self.canvas.pack(fill="both", expand=True)

        self.start_x = self.start_y = 0
        self.rect = None
        self.result = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        label = tk.Label(
            self.root,
            text=f"{prompt_text}  |  Esc to cancel",
            bg="black", fg="white", font=("Segoe UI", 14)
        )
        label.place(relx=0.5, rely=0.03, anchor="n")

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2
        )

    def on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        x1, y1 = min(self.start_x, event.x), min(self.start_y, event.y)
        x2, y2 = max(self.start_x, event.x), max(self.start_y, event.y)
        if x2 - x1 > 5 and y2 - y1 > 5:
            self.result = {"left": x1, "top": y1, "width": x2 - x1, "height": y2 - y1}
        self.root.destroy()

    def run(self):
        self.root.mainloop()
        return self.result


def pick(prompt_text):
    selector = RegionSelector(prompt_text)
    return selector.run()


if __name__ == "__main__":
    print("Step 1 of 2: select the TRIGGER region (the small spot to watch, e.g. the 'unavailable' text)")
    trigger = pick("Drag a box over the TRIGGER area (the text/spot to watch)")
    if not trigger:
        print("No trigger region selected — aborted.")
        raise SystemExit(1)
    print(f"Trigger region: {trigger}")

    print("\nStep 2 of 2: select the CAPTURE region (the larger area to screenshot when it changes)")
    capture = pick("Drag a box over the CAPTURE area (what gets screenshotted)")
    if not capture:
        print("No capture region selected — aborted.")
        raise SystemExit(1)
    print(f"Capture region: {capture}")

    with open("region.json", "w") as f:
        json.dump({"trigger": trigger, "capture": capture}, f, indent=2)
    print("\nSaved both regions to region.json.")
