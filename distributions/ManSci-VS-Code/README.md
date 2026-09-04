# ManSci VS-Code — staff-testing installer

Extract the whole ZIP to a local folder and close ManSci tools before updating.
Run **Install-Windows.bat** in Windows or **Install-Mac.command** on Mac.

**Mac security message:** “Apple could not verify…” is expected because this
installer is not Apple-notarised; it does not itself mean malware was detected.
Only for a download from your teaching team's link: click **Done**, then open
**System Settings → Privacy & Security → Security → Open Anyway** for
**Install-Mac.command**. Authenticate if asked and confirm **Open**.
Do not disable general security protections. If approval is unavailable, or a
warning says malware was detected or the software will damage your computer,
stop and contact the teaching team. Read the full explanation and troubleshooting
in **DISTRIBUTION-GUIDE.md** before proceeding.

**Windows:** those approval steps are Mac-only. Windows may display its own
installation or security prompts; a permission prompt is not a safety guarantee.
Contact the teaching team about unexpected security warnings.

The guided installer checks prerequisites first, offers installation where supported,
asks for consent to required terms, prepares Python and local AI, then creates launchers.
Keep its window open and watch for prompts. Several stages can take many minutes.
For Ollama choose **local use**, not sign-in; its service starts automatically.

Windows taskbar pins are optional: after installing a tool, find its **ManSci**
entry in Start, right-click and choose **Pin to taskbar** (possibly under **More**).
The installer never changes your pins. Pin the ManSci entry, not the ordinary
running ordinary VS Code icon. Lab now opens its own reusable window; ManSci Code
windows receive the same taskbar identity as their launcher. When upgrading from
an earlier release, manually replace old pins with the new Start entries, including
Spyder/Python pins: Spyder now also retains its ManSci identity and relaunch command.

Read **DISTRIBUTION-GUIDE.md** for the five stages, manual fallback instructions,
architecture information and automatic log locations. On failure the window stays open.
Rerun after resolving the error; student work and existing model data are preserved.

All tools share Documents/ManSci Code and mansci-python. Core supplies test.py,
test.ipynb and a folder README without overwriting existing work.
This is for staff testing, not yet approved for student rollout.
