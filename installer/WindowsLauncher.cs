// Compiled locally as a windowed executable with the tool's standard icon.
// No taskbar pinning, registry changes, elevation or network access.
using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;

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
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = config[0]; // pythonw.exe; preserve its identity for Spyder
            start.Arguments = "\"" + config[1] + "\"";
            start.WorkingDirectory = root;
            start.UseShellExecute = false;
            start.CreateNoWindow = true;
            using (Process child = Process.Start(start))
            {
                child.WaitForExit();
                if (child.ExitCode != 0)
                    throw new Exception("The tool could not start. See ManagementScience\\Logs\\launch.log in your local application-data folder.");
                return 0;
            }
        }
        catch (Exception error)
        {
            MessageBox.Show(error.Message, "ManSci launcher", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }
}
