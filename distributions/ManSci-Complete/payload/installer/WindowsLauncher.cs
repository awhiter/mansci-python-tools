// Compiled locally as a windowed executable with the tool's standard icon.
// No taskbar pinning, registry changes, elevation or network access.
using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;
using System.Collections.Generic;
using System.Management;
using System.Runtime.InteropServices;
using System.Threading;
using System.Security.Cryptography;
using System.Text;

internal static class ManSciLauncher
{
    [STAThread]
    private static int Main()
    {
        try
        {
            string root = AppDomain.CurrentDomain.BaseDirectory;
            string[] config = File.ReadAllLines(Path.Combine(root, "launcher-runtime.txt"));
            if (config.Length != 2 || !File.Exists(config[0]) || !File.Exists(config[1]))
                throw new IOException("Launcher files are missing. Please rerun the ManSci installer.");
            string settings = Path.Combine(root, "window-runtime.txt");
            string[] window = File.Exists(settings) ? File.ReadAllLines(settings) : new string[0];
            bool code = window.Length == 5 && window[0] == "VS-Code";
            bool managedWindow = window.Length == 5 && (window[0] == "Lab" || window[0] == "Spyder");
            using (Mutex gate = new Mutex(false, "Local\\ManSci." + ManSciTaskbar.PathHash(root)))
            {
            bool owned = false;
            if (code)
            {
                try { owned = gate.WaitOne(0); } catch (AbandonedMutexException) { owned = true; }
                if (!owned)
                {
                    // Another launcher owns this isolated Code profile. Do not
                    // open a second window while it is still starting.
                    for (int i = 0; i < 120; i++)
                    {
                        if (ManSciTaskbar.FocusCode(window)) return 0;
                        Thread.Sleep(1000);
                    }
                    throw new Exception("ManSci VS Code is still starting or not responding. Close it normally and retry.");
                }
                if (ManSciTaskbar.FocusCode(window) || ManSciTaskbar.ProfileIsRunning(window[2]))
                {
                    ManSciTaskbar.MonitorCode(window);
                    return 0;
                }
            }
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = config[0]; // pythonw.exe; preserve its identity for Spyder
            start.Arguments = "\"" + config[1] + "\"";
            start.WorkingDirectory = root;
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            using (Process child = Process.Start(start))
            {
                Thread watcher = null;
                if (managedWindow)
                {
                    watcher = new Thread(delegate() {
                        try { ManSciTaskbar.MonitorProcess(child, window); }
                        catch (Exception error) { File.AppendAllText(Path.Combine(root, "taskbar.log"), error.ToString() + Environment.NewLine); }
                    });
                    watcher.IsBackground = true;
                    watcher.Start();
                }
                child.WaitForExit();
                if (watcher != null) watcher.Join(2000);
                if (child.ExitCode != 0)
                    throw new Exception("The tool could not start. See ManagementScience\\Logs\\launch.log in your local application-data folder.");
                if (code) ManSciTaskbar.MonitorCode(window);
                if (owned) gate.ReleaseMutex();
                return 0;
            }
            }
        }
        catch (Exception error)
        {
            MessageBox.Show(error.Message, "ManSci launcher", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }
}

// Uses documented Shell property stores. Only ManSci-owned windows are tagged;
// no VS Code product files, pin lists, registry or other users' windows change.
public static class ManSciTaskbar
{
    [StructLayout(LayoutKind.Sequential)] private struct Key { public Guid fmtid; public uint pid; }
    [StructLayout(LayoutKind.Explicit, Size = 24)] private struct Variant
    {
        [FieldOffset(0)] public ushort vt;
        [FieldOffset(8)] public IntPtr text;
    }
    [ComImport, Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    private interface Store
    {
        [PreserveSig] int GetCount(out uint count);
        [PreserveSig] int GetAt(uint index, out Key key);
        [PreserveSig] int GetValue(ref Key key, out Variant value);
        [PreserveSig] int SetValue(ref Key key, ref Variant value);
        [PreserveSig] int Commit();
    }
    [DllImport("shell32.dll", CharSet = CharSet.Unicode, PreserveSig = false)]
    private static extern void SHGetPropertyStoreFromParsingName(string path, IntPtr context, uint flags, ref Guid iid, out Store store);
    [DllImport("shell32.dll", PreserveSig = false)]
    private static extern void SHGetPropertyStoreForWindow(IntPtr hwnd, ref Guid iid, out Store store);
    [DllImport("ole32.dll")] private static extern int PropVariantClear(ref Variant value);
    [DllImport("user32.dll")] private static extern bool EnumWindows(EnumCallback callback, IntPtr parameter);
    private delegate bool EnumCallback(IntPtr hwnd, IntPtr parameter);
    [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr hwnd, out uint pid);
    [DllImport("user32.dll")] private static extern bool IsWindowVisible(IntPtr hwnd);
    [DllImport("user32.dll")] private static extern IntPtr GetWindow(IntPtr hwnd, uint command);
    [DllImport("user32.dll")] private static extern bool IsIconic(IntPtr hwnd);
    [DllImport("user32.dll")] private static extern bool ShowWindow(IntPtr hwnd, int command);
    [DllImport("user32.dll")] private static extern bool SetForegroundWindow(IntPtr hwnd);
    [DllImport("shell32.dll", CharSet = CharSet.Unicode)] private static extern IntPtr CommandLineToArgvW(string command, out int count);
    [DllImport("kernel32.dll")] private static extern IntPtr LocalFree(IntPtr memory);
    private static Key Property(uint pid) { return new Key { fmtid = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3"), pid = pid }; }
    private static void Set(Store store, uint pid, string value)
    {
        Key key = Property(pid);
        Variant variant = new Variant { vt = 31, text = Marshal.StringToCoTaskMemUni(value) };
        try { Marshal.ThrowExceptionForHR(store.SetValue(ref key, ref variant)); }
        finally { Marshal.FreeCoTaskMem(variant.text); }
    }
    public static void SetShortcut(string path, string appId)
    {
        Guid iid = typeof(Store).GUID; Store store;
        SHGetPropertyStoreFromParsingName(path, IntPtr.Zero, 2, ref iid, out store);
        try
        {
            Set(store, 5, appId); Marshal.ThrowExceptionForHR(store.Commit());
            Key key = Property(5); Variant value;
            Marshal.ThrowExceptionForHR(store.GetValue(ref key, out value));
            try { if (Marshal.PtrToStringUni(value.text) != appId) throw new Exception("Shortcut AppUserModelID read-back failed."); }
            finally { PropVariantClear(ref value); }
        }
        finally { Marshal.ReleaseComObject(store); }
    }
    private static void Tag(IntPtr hwnd, string[] config)
    {
        Guid iid = typeof(Store).GUID; Store store;
        SHGetPropertyStoreForWindow(hwnd, ref iid, out store);
        try
        {
            // Set relaunch metadata before the identity, as required by Shell.
            Set(store, 2, "\"" + Process.GetCurrentProcess().MainModule.FileName + "\"");
            Set(store, 3, config[3] + ",0");
            Set(store, 4, config[4]);
            Set(store, 5, config[1]);
            // Window stores apply changes immediately; Commit is for files.
        }
        finally { Marshal.ReleaseComObject(store); }
    }
    public static string PathHash(string path)
    {
        using (SHA256 hash = SHA256.Create())
            return BitConverter.ToString(hash.ComputeHash(Encoding.UTF8.GetBytes(path.ToLowerInvariant()))).Replace("-", "");
    }
    public static bool MatchesProfileArgs(string[] args, string profile)
    {
        for (int i = 0; i < args.Length; i++)
        {
            string value = null;
            if (args[i] == "--user-data-dir" && i + 1 < args.Length) value = args[i + 1];
            else if (args[i].StartsWith("--user-data-dir=", StringComparison.Ordinal)) value = args[i].Substring(16);
            if (value != null && String.Equals(Path.GetFullPath(value).TrimEnd('\\', '/'), Path.GetFullPath(profile).TrimEnd('\\', '/'), StringComparison.OrdinalIgnoreCase)) return true;
        }
        return false;
    }
    private static HashSet<int> CodeProcesses(string profile)
    {
        HashSet<int> result = new HashSet<int>();
        using (ManagementObjectSearcher query = new ManagementObjectSearcher("SELECT ProcessId,CommandLine,SessionId FROM Win32_Process WHERE Name='Code.exe'"))
        foreach (ManagementObject item in query.Get())
        {
            if (Convert.ToInt32(item["SessionId"]) != Process.GetCurrentProcess().SessionId) continue;
            string line = item["CommandLine"] as string;
            if (String.IsNullOrEmpty(line)) continue;
            int count; IntPtr memory = CommandLineToArgvW(line, out count);
            if (memory == IntPtr.Zero) continue;
            try
            {
                string[] args = new string[count];
                for (int i = 0; i < count; i++) args[i] = Marshal.PtrToStringUni(Marshal.ReadIntPtr(memory, i * IntPtr.Size));
                if (!Array.Exists(args, delegate(string arg) { return arg.StartsWith("--type=", StringComparison.Ordinal); }) && MatchesProfileArgs(args, profile)) result.Add(Convert.ToInt32(item["ProcessId"]));
            }
            finally { LocalFree(memory); }
        }
        return result;
    }
    private static List<IntPtr> Windows(HashSet<int> pids)
    {
        List<IntPtr> result = new List<IntPtr>();
        EnumWindows(delegate(IntPtr hwnd, IntPtr unused) {
            uint pid; GetWindowThreadProcessId(hwnd, out pid);
            if (pids.Contains((int)pid) && IsWindowVisible(hwnd) && GetWindow(hwnd, 4) == IntPtr.Zero) result.Add(hwnd);
            return true;
        }, IntPtr.Zero);
        return result;
    }
    public static bool FocusCode(string[] config)
    {
        List<IntPtr> windows = Windows(CodeProcesses(config[2]));
        foreach (IntPtr hwnd in windows) Tag(hwnd, config);
        if (windows.Count == 0) return false;
        if (IsIconic(windows[0])) ShowWindow(windows[0], 9);
        SetForegroundWindow(windows[0]);
        return true;
    }
    public static bool ProfileIsRunning(string profile) { return CodeProcesses(profile).Count > 0; }
    public static void MonitorCode(string[] config)
    {
        DateTime deadline = DateTime.UtcNow.AddSeconds(120);
        bool seen = false;
        HashSet<IntPtr> tagged = new HashSet<IntPtr>();
        List<Process> tracked = new List<Process>();
        try
        {
        while (true)
        {
            // Discover once; retain real process handles. No repeated WMI scan
            // while Code is open, and PID reuse cannot tag an unrelated app.
            if (tracked.Count == 0)
                foreach (int pid in CodeProcesses(config[2]))
                {
                    try { Process process = Process.GetProcessById(pid); IntPtr handle = process.Handle; tracked.Add(process); }
                    catch (ArgumentException) { }
                }
            HashSet<int> pids = new HashSet<int>();
            foreach (Process process in tracked) if (!process.HasExited) pids.Add(process.Id);
            if (seen && pids.Count == 0) return;
            List<IntPtr> current = Windows(pids);
            tagged.IntersectWith(current);
            foreach (IntPtr hwnd in current)
            {
                seen = true;
                if (tagged.Add(hwnd)) Tag(hwnd, config);
            }
            if (!seen && DateTime.UtcNow > deadline) throw new Exception("ManSci VS Code did not expose a window within two minutes. See the startup logs.");
            Thread.Sleep(2000);
        }
        }
        finally { foreach (Process process in tracked) process.Dispose(); }
    }
    public static void MonitorProcess(Process process, string[] config)
    {
        HashSet<IntPtr> tagged = new HashSet<IntPtr>();
        while (!process.HasExited)
        {
            List<IntPtr> current = Windows(new HashSet<int> { process.Id });
            tagged.IntersectWith(current);
            foreach (IntPtr hwnd in current)
                if (tagged.Add(hwnd)) Tag(hwnd, config);
            Thread.Sleep(500);
        }
    }
}
