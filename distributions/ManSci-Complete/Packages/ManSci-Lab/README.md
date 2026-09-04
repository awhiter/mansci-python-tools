# ManSci Lab — staff-testing installer

Extract the whole ZIP to a local folder and close ManSci tools before updating.
Run **Install-Windows.bat** in Windows or **Install-Mac.command** on Mac.

The guided installer checks prerequisites first, offers installation where supported,
asks for consent to required terms, prepares Python and local AI, then creates launchers.
Keep its window open and watch for prompts. Several stages can take many minutes.
For Ollama choose **local use**, not sign-in; its service starts automatically.

Windows taskbar pins are optional: after installing a tool, find its **ManSci**
entry in Start, right-click and choose **Pin to taskbar** (possibly under **More**).
The installer never changes your pins. Pin the ManSci entry, not the ordinary
running VS Code/browser icon; running windows may appear separately.

Read **DISTRIBUTION-GUIDE.md** for the five stages, manual fallback instructions,
architecture information and automatic log locations. On failure the window stays open.
Rerun after resolving the error; student work and existing model data are preserved.

All tools share Documents/ManSci Code and mansci-python. Core supplies test.py,
test.ipynb and a folder README without overwriting existing work.
This is for staff testing, not yet approved for student rollout.
